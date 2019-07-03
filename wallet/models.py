from __future__ import unicode_literals
from django.conf import settings
from django.db import models
import uuid
from bitnob_utils.choices import *
import random


class Wallet(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_wallet')
    current_balance = models.BigIntegerField(default=0.00)
    currency = models.CharField(max_length=4, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.id)


class BeneficiaryBank(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_bank_account')
    bank_branch = models.CharField(max_length=50, null=True)
    bank_name = models.CharField(max_length=50, null=True)
    account_name = models.CharField(max_length=30)
    account_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bank_name


class BeneficiaryMobileMoney(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_mm_account')
    provider = models.CharField(max_length=50, null=True)
    account_name = models.CharField(max_length=30)
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.account_name


class Deposit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20)
    wallet = models.ForeignKey(Wallet,  on_delete=models.CASCADE, related_name='wallet_deposits')
    ref_code = models.CharField(unique=True, editable=False, max_length=250)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id


class ManualDeposit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, default=PENDING)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,  on_delete=models.CASCADE, related_name='user_manualdeposit')
    method = models.CharField(max_length=150, default='bank')
    ref_code = models.CharField(unique=False, editable=False, max_length=250)
    value = models.BigIntegerField(default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id


class Withdrawal(models.Model):
    """
    create withdrawal requests
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20)
    wallet = models.ForeignKey(Wallet,  on_delete=models.CASCADE, related_name='wallet_withdrawals')
    value = models.BigIntegerField(default=0.00)
    bank_account = models.ForeignKey(BeneficiaryBank,  on_delete=models.CASCADE, related_name="bank_withdrawal", null=True)
    momo_account = models.ForeignKey(BeneficiaryMobileMoney, on_delete=models.CASCADE, related_name="momo_withdrawal", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

