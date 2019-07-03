import random
from string import ascii_uppercase, digits

from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from config.settings.base import env
from bitnob_api.users.models import User
from level.models import Level
from wallet.serializers import (WalletModelSerializer,
                                DepositModelSerializer,
                                WithdrawalModelSerializer,
                                BeneficiaryBankModelSerializer,
                                BeneficiaryMobileMoneyModelSerializer,
                                ManualDepositModelSerializer,)
from wallet.models import (Wallet,
                           Deposit,
                           ManualDeposit,
                           Withdrawal,
                           BeneficiaryBank,
                           BeneficiaryMobileMoney,)

from rest_framework.decorators import list_route, detail_route
from bitnob_utils.choices import *
from bitnob_utils.funcs import *
from bitnob_utils.wallet_utils import *
import hashlib
import requests
from config.settings.base import PAYSTACK_URL, env



def validate_address(address, coin):
    url = 'https://shapeshift.io/validateAddress/' + address + '/' + coin
    res = requests.get(url)
    valid = dict(res.json())
    valid = list(valid.values())
    return valid[0]


class ManualDepositModelViewSet(ModelViewSet):
    model = ManualDeposit
    serializer_class = ManualDepositModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """get all transactions from this user's wallet """
        return ManualDeposit.objects.filter(user=self.request.user.id).order_by('-created_at')

    def create(self, request, *args, **kwargs):
        user = User.objects.get(id=request.user.id)
        wallet = Wallet.objects.get(user=user.id)
        level = Level.objects.get(id=user.level.id)
        print(request.data)
        amount = request.data['amount']
        monthly_limit = 0.00

        if user.country.currency == "NGN":
            monthly_limit = level.ng_limit

        if user.country.currency == "GHS":
            monthly_limit = level.gh_limit

        if has_exceeded_limit(wallet.id, monthly_limit, amount):
            return Response({"error": "Upgrade  account to increase your limits"},
                            status=status.HTTP_400_BAD_REQUEST)
        ref_code = "NOB" + ''.join(random.sample((ascii_uppercase + digits), 4))
        method = request.data['method']
        value = request.data['value']
        ManualDeposit.objects.create(user=request.user, method=method, value=value, ref_code=ref_code)
        return Response({"success": "Successfully Created Request"}, status=status.HTTP_201_CREATED)

    @detail_route(methods=['PUT'])
    def paid_request(self, request, pk=None):
        instance = self.get_object()
        instance.status = PROCESSING
        instance.save()
        return Response("Deposit Request Submitted")


class DepositModelViewSet(ModelViewSet):
    model = Deposit
    serializer_class = DepositModelSerializer
    permission_classes = [IsAuthenticated]

    """
    voucher_deposit:
    Deposit using Bitnob Gift Card
    
    """
    def get_queryset(self):
        return Deposit.objects.filter(wallet__user=self.request.user.id)

    @list_route(methods=['POST'])
    def voucher_deposit(self, request):
        # send voucher pin to Voucher API to confirm validity
        check_voucher = validate_pin(request.data['voucher_code'])
        if not check_voucher:
            return Response({"error": "This Voucher does not exists"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"test": "Found it"}, status=status.HTTP_201_CREATED)


class WithdrawalModelViewSet(ModelViewSet):
    model = Withdrawal
    serializer_class = WithdrawalModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Withdrawal.objects.filter(wallet__user=self.request.user.id)

    def create(self, request, *args, **kwargs):
        """
        mental note: find best way to query for wallet, should we take the wallet based on the user or from the request
        :param request:
        :param args:
        :param kwargs:
        :return: serialized object
        """
        wallet = Wallet.objects.filter(user=self.request.user.id)
        wallet = Wallet.objects.get(id=wallet)
        request.data['status'] = PENDING

        if request.data['value'] > wallet.current_balance:
            return Response("Insufficient Balance")
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            wallet.current_balance = wallet.current_balance - request.data['value']
            wallet.save()
            return Response(serializer.data)


class WalletModelViewSet(ModelViewSet):
    model = Wallet
    serializer_class = WalletModelSerializer
    permission_classes = [IsAuthenticated]

    """
    request_pay_link:
    Request Payment link
    
    """

    def get_queryset(self):
        return Wallet.objects.filter(user=self.request.user.id)

    @csrf_exempt
    @list_route(methods=['POST'], permission_classes=[AllowAny])
    def request_pay_link(self, request):
        user = User.objects.get(id=request.user.id)
        wallet = Wallet.object.get(user=user.id)
        level = Level.objects.get(id=user.level.id)
        print(total_deposits(wallet.id))
        if total_deposits(wallet.id) >= level.max_limit:
            return Response({"error": "You have Exceeded your limit, upgrade your account to increase limits"},
                            status=status.HTTP_400_BAD_REQUEST)

        validated_address = validate_address(request.data['address'], 'BTC')

        if not validated_address:
            return Response({"error": "Address is invalid"},
                            status=status.HTTP_400_BAD_REQUEST)
        url = "https://voguepay.com/"
        headers = {'Content-Type': 'application/json'}
        amount = request.data['amount']

        if request.data['currency'] == "NGN":
            amount_to_pay = amount * settings.NAIRA
        if request.data['currency'] == "GHS":
            amount_to_pay = amount * settings.CEDIS

        payload = {
            "total": amount_to_pay,
            "memo": "Bitnob Deposit",
            "name": 'Bitnob',
            "cur": request.data['currency'],
            "v_merchant_id": env(),
            "merchant_ref": "BTBDEP" + ''.join(random.sample((ascii_uppercase + digits), 4)),
            "p": "linkToken",
            "value": request.data['amount']
        }
        response = requests.get(url, params=payload, headers=headers)
        return Response({'payurl': response.text, 'payload': payload})

    @detail_route(methods=['PUT'])
    def vogue_pay_request(self, request, pk=None):
        user = User.objects.get(id=request.user.id)
        wallet = Wallet.objects.get(user=user.id)
        level = Level.objects.get(id=user.level.id)
        amount = request.data['amount']
        monthly_limit = 0.00
        if user.country.currency == "NGN":
            monthly_limit = level.ng_limit
        if user.country.currency == "GHS":
            monthly_limit = level.gh_limit

        if has_exceeded_limit(wallet.id, monthly_limit, amount):
            return Response({"error": "Upgrade  account to increase your limits"},
                            status=status.HTTP_400_BAD_REQUEST)

        url = "https://voguepay.com/"
        headers = {'Content-Type': 'application/json'}
        payload = {
            "total": amount,
            "memo": "Funds Deposit by ",
            "name": request.user.first_name + ' ' + request.user.last_name,
            "email": request.user.email,
            "developer_code": "ddd",
            "cur": request.data['currency'],
            # "v_merchant_id": "demo",
            "v_merchant_id": env('VOGUEPAY_KEY'),
            # "v_merchant_id": "1045-0068218",
            "merchant_ref": "BTBDEP" + ''.join(random.sample((ascii_uppercase + digits), 4)),
            "p": "linkToken"
        }
        print(payload)
        response = requests.get(url, params=payload, headers=headers)
        return Response({'payurl': response.text, 'payload': payload})

    @list_route(methods=['POST'])
    def get_payment_info(self, request):
        instance = Wallet.objects.get(id=request.data['wallet'])
        id = request.data['transaction_id']
        url = 'https://voguepay.com/?v_transaction_id=' + id + '&type=json&demo=true'
        response = requests.get(url).json()
        total = float(response['total_credited_to_merchant'])
        instance.current_balance += total
        instance.save()
        ref = "BTBDEP" + ''.join(random.sample((ascii_uppercase + digits), 4))
        deposit = Deposit(wallet=instance, value=total, status=COMPLETED,  ref_code=ref)
        deposit.save()
        ManualDeposit.objects.create(user=request.user, status=COMPLETED, method="debit_card", value=total, ref_code=ref)
        return Response('Successfully Deposited Funds')

    @list_route(methods=['POST'])
    def verify_paystack_payment(self, request):
        """
        Verify a paystack transaction and fund the user wallet if valid
        :param request:
        :return:
        """
        instance = Wallet.objects.get(id=request.data['wallet'])
        transaction_id = request.data['transaction_id']
        headers = {"Authorization":  env('PAYSTACK_SECRET')}
        url = PAYSTACK_URL + 'transaction/verify/' +  transaction_id
        response = requests.get(url, headers=headers).json()
        # print(response)
        total = int(response['data']['amount']) / 100
        instance.current_balance += total
        ref_code = "BTBDEP" + ''.join(random.sample((ascii_uppercase + digits), 4))
        instance.save()
        deposit = Deposit(wallet=instance,
                          value=total,
                          ref_code=ref_code)
        deposit.save()
        return Response({"tx": response}, status=status.HTTP_200_OK)

    @detail_route(methods=['PUT'], serializer_class=DepositModelSerializer)
    def deposit(self, request, pk=None):
        instance = self.get_object()
        ref_code = ''.join(random.sample((ascii_uppercase + digits), 8))
        deposit = Deposit(wallet=instance,
                          value=request.data['value'],
                          ref_code=ref_code)
        serializer = self.get_serializer(data=deposit)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BeneficiaryBankModelViewSet(ModelViewSet):
    model = BeneficiaryBank
    serializer_class = BeneficiaryBankModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BeneficiaryBank.objects.filter(user=self.request.user)


class BeneficiaryMobileMoneyModelViewSet(ModelViewSet):
    model = BeneficiaryMobileMoney
    serializer_class = BeneficiaryMobileMoneyModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return BeneficiaryMobileMoney.objects.filter(user=self.request.user)


class AdminWalletModelViewSet(ModelViewSet):
    model = Wallet
    serializer_class = WalletModelSerializer
    permission_classes = [IsAdminUser]
    queryset = Wallet.objects.all()

    """
    empty_wallets:
    No of wallets without any funds
    
    funded_wallets:
    No of currently funded wallets
    
    unfunded_wallets:
    No of wallets that have never been funded
    
    busiest_wallets:
    Wallets with the highest number of deposits e.g top 5
    
    top_funded_wallets:
    Wallets that have been funded the most
    
    no_withdrawal_requests:
    No of withdrawal requests
    
    total_deposits:
    Total Amount deposited
    
    total_withdrawals:
    Total Amount withdrawn
    
    total_pending withdrawals:
    Total Amounts pending withdrawal
    
    """





