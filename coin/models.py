from django.db import models
from django.template.defaultfilters import slugify
from bitnob_utils.choices import *


class Coin(models.Model):
    name = models.CharField(max_length=20, unique=True)
    slug = models.SlugField(max_length=20, unique=True)
    symbol = models.CharField(max_length=3, unique=True)
    logo = models.URLField(blank=False, unique=True)
    buy_rate = models.DecimalField(decimal_places=2, max_digits=5)
    purchase_price = models.DecimalField(decimal_places=2, max_digits=8, default=0.00)
    sell_rate = models.DecimalField(decimal_places=2, max_digits=6)
    fees = models.DecimalField(decimal_places=2, max_digits=16, default=0.00)
    status = models.CharField(max_length=10, default=INACTIVE)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def slug(self):
        return slugify(self.name)

