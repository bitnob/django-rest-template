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


@python_2_unicode_compatible
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=15, null=True,
                             help_text=_("Phone number of the user"))


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
    """
     signal to log user logins
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ipaddress = x_forwarded_for.split(',')[-1].strip()
    else:
        ipaddress = request.META.get('REMOTE_ADDR')

    browser = request.META.get('HTTP_USER_AGENT')
    browser = str(browser)
    UserLoginHistory.objects.create(action='user_logged_in', ip=ipaddress, user=user, browser=browser)


class Referral(models.Model):
    referrer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_referrer')
    referred = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_referred')
    created = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('referrer', 'referred'),)
