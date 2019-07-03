import uuid
from django.conf import settings
from django.db import models
from django.apps import apps
from bitnob_api.users.models import *
# from bitnob_api.users.models import UserData
from country.models import Country


# UserData = apps.get_models('bitnob_api.users', 'UserData')


class Level(models.Model):
    """
    user : Admin user who added or edited this level
    name : Name of this level
    discount: All user on this level enjoy this % discount which can be changed periodically by an admin
    max_limit: The maximum amount every user on this level can purchase at that level
    daily_limit: Max amount that can be purchased daily
    monthly_limit: Max amount that can be purchased monthly

    TODO
    1. set default user level
    2. view for user level request upgrade
    3. view for approving user level upgrade request
    4. views to list all  users according to their levels
    """

    id = models.UUIDField(primary_key=True,
                          default=uuid.uuid4,
                          editable=False)
    name = models.CharField(max_length=100, null=False)
    max_limit = models.DecimalField(max_digits=16, decimal_places=2)
    daily_limit = models.DecimalField(max_digits=16, decimal_places=2)
    monthly_limit = models.DecimalField(max_digits=16, decimal_places=2)
    discount = models.DecimalField(max_digits=16, decimal_places=2)
    trading_fees = models.DecimalField(max_digits=16, decimal_places=2, default=0.00)
    ng_limit = models.DecimalField(max_digits=16, decimal_places=2, null=True, default=0.00)
    gh_limit = models.DecimalField(max_digits=16, decimal_places=2, null=True, default=0.00)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class LevelUpgradeRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE,
                             related_name='user')
    # user_data = models.ForeignKey(UserData,
    #                          on_delete=models.CASCADE,
    #                          related_name='user_data')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                    on_delete=models.CASCADE,
                                    related_name='approval_user')
    approved = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    address = models.CharField(max_length=100, null=True, help_text="The Home Address of the user")
    utility_bill = models.TextField(null=True, max_length=400)
    social_account = models.URLField(null=True, max_length=400)
    selfie = models.TextField(null=True, max_length=400)
    bvn = models.CharField(null=True, max_length=400)
    dob = models.CharField(null=True, max_length=400)
    govt_id = models.TextField(null=True, max_length=400)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

    @property
    def level(self):
        print(self.user.level.name)
        level = Level.objects.get(name=self.user.level.name)
        return level.name



class Referral(models.Model):
    name = models.CharField(max_length=100, null=False)

    def __str__(self):
        return self.name

