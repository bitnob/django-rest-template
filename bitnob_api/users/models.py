# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import
from datetime import datetime
import uuid
import random
from string import ascii_uppercase, digits
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from allauth.account.signals import user_signed_up
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.conf import settings

from coin.models import Coin
from wallet.models import Wallet
from country.models import Country
from level.models import Level


@python_2_unicode_compatible
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, null=True,
                             help_text=_("Phone number. Usually saved after the user has verified by sms"))
    address = models.CharField(max_length=100, null=True, help_text=_("The Address of the user"))
    sms_conf = models.CharField(max_length=20, null=True)
    referral_code = models.CharField(max_length=260, null=True, unique=True, help_text="User referral code")
    verification_in_progress = models.BooleanField(default=False, help_text=_("The user is still getting verified"))
    verification_completed = models.BooleanField(default=False, help_text=_("The user has been verified"))
    verified_phone = models.BooleanField(default=False, help_text=_("The user has verified their phone number"))
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='level',
                              help_text=_("The current level of the user"))
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='country',
                                help_text=_("The user's country"))


    def __str__(self):
        return self.username


class UserLoginHistory(models.Model):
    action = models.CharField(max_length=64)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_login')
    ip = models.GenericIPAddressField(null=True, default='0.0.0.0', help_text=_("The login ip address of the user"))
    browser = models.CharField(max_length=256, null=True, help_text=_("Type of browser used"))
    time = models.DateTimeField(auto_now_add=True, help_text=_("Time login occured"))

    class Meta:
        ordering = ('-time',)

    def __str__(self):
        return '{0} - {1} - {2}'.format(self.action, self.username, self.ip)


@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    # if user does not have a wallet, create it for them
    if not Wallet.objects.filter(user=user).exists():
        user_wallet = Wallet(user=user, current_balance=0.00)
        user_wallet.save()

    if  user.referral_code is None:
        user.referral_code = settings.URL_FRONT + 'signup?ref=' + ''.join(random.sample((ascii_uppercase+digits), 9))
        user.save()
    user.referral_code = settings.URL_FRONT + 'signup?ref=' + ''.join(random.sample((ascii_uppercase+digits), 9))
    user.save()
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ipaddress = x_forwarded_for.split(',')[-1].strip()
    else:
        ipaddress = request.META.get('REMOTE_ADDR')

    browser = request.META.get('HTTP_USER_AGENT')
    browser = str(browser)
    UserLoginHistory.objects.create(action='user_logged_in', ip=ipaddress, user=user, browser=browser)


class UserData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    address = models.CharField(max_length=100, null=True, help_text=_("The Home Address of the user"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_kyc')
    utility_bill = models.TextField(null=True, max_length=400)
    social_account = models.URLField(null=True, max_length=400)
    selfie = models.TextField(null=True, max_length=400)
    bvn = models.CharField(null=True, max_length=400)
    dob = models.CharField(null=True, max_length=400)
    govt_id = models.TextField(null=True, max_length=400)

    def __str__(self):
        return self.id


class DepositAddress(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_deposit_address')
    address = models.CharField(max_length=230)
    coin = models.ForeignKey(Coin,  on_delete=models.CASCADE,  related_name="deposit_coin")
    created = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.address


class UserReferral(models.Model):
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_referrer')
    referred = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_referred')
    created = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('referrer', 'referred'),)
