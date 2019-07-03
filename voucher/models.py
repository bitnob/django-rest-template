from django.db import models
from fernet_fields import EncryptedCharField


class Voucher(models.Model):
    code = EncryptedCharField(unique=True)
    value = models.BigIntegerField(default=0.00, null=False)
    used = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.code
