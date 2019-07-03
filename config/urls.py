# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf import settings
from django.urls import include, path
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework_jwt.views import refresh_jwt_token
from rest_framework import routers
from rest_framework.documentation import include_docs_urls
from orders.views import BuyOrdersModelViewSet, SellOrderModelViewSet
from bitnob_api.users.views import (UserModelViewSet,
                                    null_view,
                                    confirm_email,
                                    UserLoginHistoryModelViewSet,
                                    APIHome,
                                    AdminUserModelViewSet)

from coin.views import PublicCoinListModelViewSet, AdminCoinModelViewSet
from country.views import PublicCountryModelViewSet, AdminCountryModelViewSet

from wallet.views import (AdminWalletModelViewSet,
                          WalletModelViewSet,
                          BeneficiaryBankModelViewSet,
                          BeneficiaryMobileMoneyModelViewSet,
                          ManualDepositModelViewSet,
                          WithdrawalModelViewSet,
                          DepositModelViewSet)

from level.views import (LevelModelViewSet,
                         AdminLevelModelViewSet,
                         AdminLevelUpgradeRequestModelViewSet,
                         UpgradeLevelRequestModelViewSet,
                         LevelUpgradeRequestModelViewSet)


from bitnob_api.users.views import UserStatsModelViewSet
from stats.views import StatModelViewSet

router = routers.DefaultRouter()
# admin_router = routers.DefaultRouter()

router.register(r'coins', PublicCoinListModelViewSet, base_name='coins')
router.register(r'users', UserModelViewSet, base_name='user_acct')
router.register(r'wallets', WalletModelViewSet, base_name='wallets')
router.register(r'buy', BuyOrdersModelViewSet, base_name='buy_orders')
router.register(r'sell', SellOrderModelViewSet , base_name='sell_orders')
router.register(r'countries', PublicCountryModelViewSet, base_name='public_countries')
router.register(r'user_bank_accts', BeneficiaryBankModelViewSet, base_name='beneficiary_bank_accounts')
router.register(r'user_momo_accts', BeneficiaryMobileMoneyModelViewSet, base_name='beneficiary_momo_accounts')
router.register(r'deposits', DepositModelViewSet, base_name='deposits')
router.register(r'manual_deposit', ManualDepositModelViewSet, base_name='manual_deposits')
router.register(r'withdrawals', WithdrawalModelViewSet, base_name='withdrawals')
router.register(r'upgrade_level', LevelUpgradeRequestModelViewSet, base_name='user_level_upgrade')

router.register(r'admin/wallets', AdminWalletModelViewSet, base_name='admin_wallets')
router.register(r'admin/coins', AdminCoinModelViewSet, base_name='admin_coins')
router.register(r'admin/countries', AdminCountryModelViewSet, base_name='admin_countries')
router.register(r'admin/levels', AdminLevelModelViewSet, base_name='admin_levels')
router.register(r'admin/users', AdminUserModelViewSet)
router.register(r'admin/account/upgrades-requests', AdminLevelUpgradeRequestModelViewSet, base_name='admin_levels_upgrade')
# router.register(r'admin/levels/upgrades', AdminLevelUpgradeRequestModelViewSet, base_name='admin_levels_upgrade')

#1A9bHfrwcXw3WN3PbaV9m1GdUnwShTvkEo

router.register(r'admin/stats', StatModelViewSet, base_name='stats')

# https://res.cloudinary.com/py/image/upload/v1516641408/bitcoin_logo_31993-600x337_vk3vpu.jpg

urlpatterns = [
    url(settings.ADMIN_URL, admin.site.urls),
    # url('', include('rest_framework_docs.urls')),
    url('', include(router.urls)),
    url(r'^accounts/', include('allauth.urls')),
      # auth urls
    url(r'^rest-auth/registration/account-email-verification-sent/', null_view,
          name='account_email_verification_sent'),
    url(r'^rest-auth/registration/account-confirm-email/', null_view, name='account_confirm_email'),
    url(r'^password-reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
         null_view, name='password_reset_confirm'),
    url(r'^api/v1/rest-auth/', include('rest_auth.urls')),
    url(r'^verify-email/(?P<key>\w+)/$', confirm_email, name="account_confirm_email"),
    url(r'^api/v1/rest-auth/registration/', include('rest_auth.registration.urls')),
    url(r'^auth/v1/api-token-auth/', obtain_jwt_token),
    # path('o/', include('oauth2_provider.urls', namespace='oauth2_provider')),
    url(r'^api-token-refresh/', refresh_jwt_token),
    # url(r'^docs/', include('rest_framework_docs.urls')),
    url('bitnobdocs/', include_docs_urls(title='Bitnob API Documentation')),
    url(r'api/v1/', include(router.urls)),
    # path('api/v1/admin', include(admin_router.urls)),

] + static(
    settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [

    ]

    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
#
#

