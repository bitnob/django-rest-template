from __future__ import absolute_import, unicode_literals
from allauth.account.views import ConfirmEmailView
from django.http import JsonResponse
from django.db.models import Sum, Aggregate, Avg, Count
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.views import APIView
from .models import User, UserLoginHistory, UserData
from .serializers import (
    UserModelSerializer,
    VerifyEmailSerializer,
    UserLoginHistorySerializer,
)
from django.views.generic.base import TemplateView
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    list_route,
    detail_route
)
from rest_framework.response import Response
from random import randint


class APIHome(TemplateView):
    template_name = '404.html'


@api_view()
def null_view(request):
    return Response(status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView, ConfirmEmailView):
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs['key'] = serializer.validated_data['key']
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        return Response({'detail': _('ok')}, status=status.HTTP_200_OK)


confirm_email = VerifyEmailView.as_view()


class MultiSerializerViewSetMixin(object):
    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super(MultiSerializerViewSetMixin, self).get_serializer_class()


class UserModelViewSet(ModelViewSet):
    """
    User Endpoints

    """
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = UserModelSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

class UserLoginHistoryModelViewSet(ModelViewSet):
    """
    Login history of the logged in user
    """
    model = UserLoginHistory
    serializer_class = UserLoginHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserLoginHistory.objects.filter(user=self.request.user)
