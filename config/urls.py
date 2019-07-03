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


from app_api.users.views import UserModelViewSet

router = routers.DefaultRouter()
admin_router = routers.DefaultRouter()

router.register(r'users', UserModelViewSet, base_name='users')


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
    url('appdocs/', include_docs_urls(title='app API Documentation')),
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

