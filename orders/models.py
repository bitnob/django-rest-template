import json
import uuid
from django.db import models
from django.conf import settings
from coin.models import Coin
from bitnob_utils.choices import *
from django.utils import timezone
import datetime
import pytz

datetime.datetime.now(tz=timezone.utc)


def invoice_expiry():
    d1 = datetime.datetime.now() + datetime.timedelta(minutes=15)
    return d1


class BuyOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_user')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coin = models.ForeignKey(Coin,  on_delete=models.CASCADE,  related_name="coin")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.CharField(max_length=256)
    transaction_id = models.CharField(max_length=256)
    reference_id = models.CharField(max_length=256, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.transaction_id


class QuickServe(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    email = models.EmailField()
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.CharField(max_length=256)
    transaction_id = models.CharField(max_length=256)
    reference_id = models.CharField(max_length=256, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id

class SellOrder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sellorder_user')
    amount_sold = models.DecimalField(max_digits=10, decimal_places=2)
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # value in local currency user will receive
    coin = models.ForeignKey(Coin,  on_delete=models.CASCADE,  related_name="sell_coin")
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.CharField(max_length=256, null=True, blank=True)
    transaction_id = models.CharField(max_length=256, null=True, blank=True)
    reference_id = models.CharField(max_length=256, unique=True)
    created = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)


class Invoice(models.Model):
    """
    Invoice for sending BTC to Bitnob
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_invoice')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    local_value = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    btc_amount = models.DecimalField(max_digits=20, decimal_places=8, default=0.000000000)
    reference_id = models.CharField(max_length=256, unique=True)
    wallet_address = models.CharField(max_length=256)
    fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(default=UNPAID, max_length=230)
    expiry = models.DateTimeField(default=invoice_expiry)
    created = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.reference_id
