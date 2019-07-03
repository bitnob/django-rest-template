import json

from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView
from rest_framework import status
from rest_framework.response import Response

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny

from bitnob_api.users.models import DepositAddress, User
from bitnob_utils.exchange_rates import get_price
from bitnob_utils.funcs import validate_pin
from bitnob_utils.invoice_utils import generate_address, get_payment_status
from .serializers import CoinModelSerializer, AdminCoinModelSerializer
from .models import Coin
from bitnob_utils.choices import *
from bitnob_utils.process_order import *
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope, TokenHasScope


"""
Todos
1. set permissions for who can update rates
2.keep track of rates history
"""


class PublicCoinListModelViewSet(ReadOnlyModelViewSet):
    """
     Show listed coins/tokens on bitnob
    """
    model = Coin
    queryset = Coin.objects.all()
    serializer_class = CoinModelSerializer
    permission_classes = [TokenHasScope]
    required_scopes = []

    @csrf_exempt
    @list_route(methods=['POST'], permission_classes=[AllowAny])
    def calculate_local(self, request):
        """
        This endpoint is for the quick service API to validate a voucher and show the user the amount of BTC they
        will be receiving

        There is a 2% premium for using the service


        :param request:
        :return:
        """
        pin = request.data['pin']
        voucher = validate_pin(pin)
        amount = 0.00
        if not voucher:
            return Response({"error": "This voucher does not exist"}, status=status.HTTP_400_BAD_REQUEST)

        if voucher['valid']:
            if voucher['voucher']['used']:
                return Response({"error": "This voucher has already been used"}, status=status.HTTP_400_BAD_REQUEST)

            if not voucher['voucher']['used']:
                amount = voucher['voucher']['value']
                fees = calculate_service_fees(amount)
                amount -= fees
                params = {
                            'value': amount,
                            'currency': 'USD'
                }
                satoshi = requests.get("https://blockchain.info/tobtc", params=params)
                return Response({"satoshi": float(satoshi.text)}, status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def get_sats(self, request):
        """
        :param request:
        :return:
        """
        coin = Coin.objects.get(symbol="BTC")
        amount = request.data['amount']
        current_price = get_price()

        validated_address = validate_address(request.data['address'], coin.symbol)
        if not validated_address:
            return Response({"error": "Address is invalid"},
                            status=status.HTTP_400_BAD_REQUEST)

        if amount < 10:
            return Response({"error": "Amount is less than minimum allowed"},
                            status=status.HTTP_400_BAD_REQUEST)

        sats = to_btc(amount)  # you will get the same amount you wanted alright?
        local_cost = calculate_total_cost("BTC", amount, request.data['currency'], coin.purchase_price, current_price)
        fees = calculate_service_fees(local_cost)
        return Response({'sats': sats, 'fees': fees, 'total': local_cost}, status=status.HTTP_200_OK)

    @list_route(methods=['POST'])
    def get_sats_for_sell(self, request):
        """
        :param request:
        :return:
        """
        coin = Coin.objects.get(symbol="BTC")
        amount = request.data['amount']
        current_price = get_price()
        user = User.objects.get(id=request.user.id)
        deposit_address = DepositAddress.objects.filter(user=user.id).values('address')[0]

        if amount < 10:
            return Response({"error": "Amount is less than minimum you can sell"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            deposit_address = DepositAddress.objects.filter(user=user.id).values('address')[0]
            # deposit_address = deposit_address.values('address')
            return deposit_address
        except ObjectDoesNotExist:
            create_address = DepositAddress(user=user,
                                            address=generate_address(),
                                            coin=coin)
            create_address.save()
            deposit_address = create_address.address
            return deposit_address
        finally:
            sats = to_btc(amount)
            get_payment_status(deposit_address['address'])
            local_cost = calculate_total_cost_of_purchase("BTC", amount, request.data['currency'], coin.purchase_price, current_price)
            return Response({'sats': sats,
                             'total': local_cost,
                             'current_price': current_price,
                             'address': deposit_address}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def get_rates(self, request):
        price = get_price()
        local_cost = exchange_rate("BTC", request.data['currency'])
        return Response({'price': price, 'local_cost': local_cost}, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def prices(self, request):
        price = get_price()
        return Response({'price': price}, status=status.HTTP_200_OK)



# class CoinListModelView(ListView):
#     model = Coin
#     queryset = Coin.objects.all()
#     serializer_class = [IsAuthenticated]


# display price that is good
# reduce charges when posting to API for satoshi value


class AdminCoinModelViewSet(ModelViewSet):
    """
    activate_coin:
    Change state of the coin to active
    send `id`  to endpoint
    **Method**: `POST`


    deactivate_coin:
    Change state of coin to inactive
    send `id`  to endpoint
    **Method**: `POST`

    """
    model = Coin
    queryset = Coin.objects.all()
    serializer_class = AdminCoinModelSerializer
    permission_classes = [IsAuthenticated]

    @list_route(methods=["POST"])
    def activate_coin(self, request):
        coin = Coin.objects.get(id=request.data['id'])
        coin.status = ACTIVE
        coin.save()
        return Response({"success": "Successfully changed  coin status"})

    @list_route(methods=["POST"])
    def deactivate_coin(self, request):
        coin = Coin.objects.get(id=request.data['id'])
        coin.status = INACTIVE
        coin.save()
        return Response({"success": "Successfully changed  coin status"})

