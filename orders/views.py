import random
from string import ascii_uppercase, digits
import json
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage
from django.db.models import Sum
from django.template.loader import get_template

from bitnob_api.users.models import User, DepositAddress
from bitnob_utils.funcs import validate_pin, change_voucher_status
from bitnob_utils.process_order import *
from bitnob_utils.exchange_rates import *
from bitnob_utils.invoice_utils import *
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from bitnob_api.users.serializers import UserModelSerializer
from .serializers import (
    BuyOrderModelSerializer,
    InvoiceModelSerializer)
from .models import BuyOrder, SellOrder, Invoice, QuickServe
from rest_framework.decorators import list_route, detail_route
from wallet.models import Wallet
from coin.models import Coin
import requests
from config.settings.base import env


class BuyOrdersModelViewSet(ModelViewSet):
    model = BuyOrder
    serializer_class = BuyOrderModelSerializer
    permission_classes = [IsAuthenticated]

    """
    stats:
    returns the user's transaction statistics such as total spent purchases, number of transactions etc
    """

    def get_queryset(self):
        return BuyOrder.objects.filter(user=self.request.user).order_by('-modified_on')

    def create(self, request, *args, **kwargs):
        # generate a random unique value as order reference
        user = User.objects.get(id=request.user.id)
        coin = Coin.objects.get(symbol="BTC")
        amount = request.data['amount']
        request.data['reference_id'] = settings.BUY_ORDER_PREFIX \
                                       + ''.join(random.sample((ascii_uppercase+digits), 4))\
                                       + 'L'
        validated_address = validate_address(request.data['address'], 'BTC')
        user_account_balance = get_account_balance(user.id)
        total_cost = calculate_total_cost("BTC", amount, request.data['currency'], coin.purchase_price, get_price())
        total_cost += calculate_service_fees(total_cost)

        if total_cost > user_account_balance:
            return Response({"error": "Insufficient Funds"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not validated_address:
            return Response({"error": "Address is invalid"},
                            status=status.HTTP_400_BAD_REQUEST)

        if request.data['amount'] < 10:
            return Response({"error": "Amount is less than minimum allowed"},
                            status=status.HTTP_400_BAD_REQUEST)

        else:
            params = {
                'address': request.data['address'],
                'amount': request.data['amount']
            }

            headers = {'content-type': 'application/json'}
            send_btc = requests.post(env('WALLET_BASE_URL'), data=params, params=params, headers=headers).json()
            if send_btc['success']:
                request.data['fee'] = send_btc['fee']
                request.data['cost'] = total_cost
                request.data['transaction_id'] = send_btc['txid']
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = User.objects.get(id=request.user.id)
                coin = Coin.objects.get(id=request.data['coin'])
                order = BuyOrder(user=user,
                                 cost=total_cost,
                                 transaction_id=send_btc['txid'],
                                 fee=send_btc['fee'],
                                 address=request.data['address'],
                                 coin=coin,
                                 amount=request.data['amount'],
                                 reference_id=request.data['reference_id']
                                 )
                order.save()
                debit_wallet(total_cost, user)
                return Response(
                    {"success": "Successfully Sent  BTC"},
                    status=status.HTTP_201_CREATED,
                )
            else:
                return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @list_route(methods=['POST'], permission_classes=[AllowAny])
    def send(self, request):
        """
        Quick Service Endpoint
        Send request to voucher api
        Voucher API validates voucher and sends request to trading engine to send the Bitcoins to the user
        :param request:
        :return:
        """
        # coin = Coin.objects.get(symbol="BTC")
        pin = request.data['pin']
        headers = {'content-type': 'application/json'}
        reference = settings.QUICKSERVE + ''.join(random.sample((ascii_uppercase+digits), 4)) + 'B'
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
                address = request.data['address']

                params = {
                    'address': address,
                    'amount': amount
                }
                send_btc = requests.post(
                    env('WALLET_BASE_URL'),
                    data=params, params=params, headers=headers).json()

                if send_btc['success']:
                    # mark voucher used on voucher server to prevent double spend
                    change_voucher_status(voucher['voucher']['pin'])
                    txid = send_btc['txid']
                    pin = voucher['voucher']['pin']
                    amount = voucher['voucher']['value']
                    subject = "Bitnob  Voucher Transaction"
                    to = [request.data['email']]
                    from_email = 'support@bitnob.com'
                    ctx = {
                        'txid': txid
                    }
                    message = get_template('emails/quick_service.html').render(ctx)
                    msg = EmailMessage(subject, message, to=to, from_email=from_email)
                    msg.subject = subject
                    msg.content_subtype = 'html'
                    msg.send()
                    order = QuickServe(transaction_id=txid,
                                       email=request.data['email'],
                                       address=address,
                                       fee=fees,
                                       amount=amount,
                                       reference_id=reference,
                                       )
                return Response({"txid": txid}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "Transaction Failed, Try again or contact support"},
                                status=status.HTTP_400_BAD_REQUEST)

    @list_route(methods=['GET'])
    def stats(self, request):
        no_of_orders = BuyOrder.objects.filter(user=self.request.user.id).count()
        total_spent = list(BuyOrder.objects.all().aggregate(Sum('cost')).values())[0] or 0.00
        return Response({
            "no_of_orders": no_of_orders,
            "total_spent": total_spent
        }, status=status.HTTP_200_OK)


class SellOrderModelViewSet(ModelViewSet):
    model = Invoice
    serializer_class = InvoiceModelSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Invoice.objects.filter(user=self.request.user).order_by('-created')

    @csrf_exempt
    @list_route(methods=['POST', 'GET'])
    def payment_notification(self, request):
        status = get_payment_status(request.data['address'])
        return Response(status)

    @csrf_exempt
    @list_route(methods=['POST', 'GET'],
                permission_classes=[AllowAny])
    #add invoice id to callback
    def receive_callback(self, request):
        print(request.query_params)

        return Response(status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        coin = Coin.objects.get(symbol="BTC")
        try:
            deposit_address = DepositAddress.objects.filter(user=user.id).values('address')[0]
            # deposit_address = deposit_address.values('address')
            print(deposit_address)
            return deposit_address
        except ObjectDoesNotExist:
            create_address = DepositAddress(user=user,
                                            address=generate_address(),
                                            coin=coin)
            create_address.save()
            deposit_address = create_address.address
            return deposit_address
        finally:
            amount = request.data['amount']
            request.data['reference_id'] = settings.SELL_ORDER_PREFIX \
                                           + ''.join(random.sample((ascii_uppercase+digits), 4))\
                                           + 'L'
            value = calculate_total_cost_of_purchase("BTC", amount, request.data['currency'], coin.purchase_price, get_price())

            if request.data['amount'] < 10:
                return Response({"error": "Amount is less than minimum allowed"},
                                status=status.HTTP_400_BAD_REQUEST)

            else:
                # coin = Coin.objects.get(id=request.data['coin'])
                # serializer = self.get_serializer(data=request.data)
                # serializer.is_valid(raise_exception=True)
                # order = SellOrder(user=user,
                #                   fee=0.00,
                #                   address="1A9bHfrwcXw3WN3PbaV9m1GdUnwShTvkEo",
                #                   coin=coin,
                #                   amount_sold=request.data['amount'],
                #                   value=value,
                #                   transaction_id='',
                #                   reference_id=request.data['reference_id'])
                # request.data['wallet_address'] = generate_address()
                # request.data['btc_amount'] = request.data['satoshi']
                # request.data['local_value'] = request.data['total']
                # print(request.data)

                invoice = Invoice(user=user,
                                  wallet_address=deposit_address,
                                  btc_amount=request.data['satoshi'],
                                  local_value=request.data['total'],
                                  amount=amount,
                                  reference_id=request.data['reference_id'])

                # invoice.save()
                # invoice = Invoice.objects.get(reference_id=invoice.reference_id)
                # self.perform_create()
                #show this to user
                invoice = {
                    'wallet_address': deposit_address,
                    'local_value': invoice.local_value,
                    'btc_amount': invoice.btc_amount,
                    'amount': amount,
                    'current_price': get_price()
                }
                return Response(
                    {"invoice": invoice},
                    status=status.HTTP_201_CREATED,
                )

    @list_route(methods=['GET'])
    def stats(self, request):
        no_of_orders = BuyOrder.objects.filter(user=self.request.user.id).count()
        total_spent = list(BuyOrder.objects.all().aggregate(Sum('cost')).values())[0] or 0.00
        return Response({
            "no_of_orders": no_of_orders,
            "total_spent": total_spent
        }, status=status.HTTP_200_OK)



