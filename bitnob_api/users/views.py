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
    AdminUserModelSerializer,
    UserLoginHistorySerializer,
    UserWalletModelSerializer
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
# import cloudinary
# import cloudinary.uploader
# import cloudinary.api
from bitnob_utils.kyc import *
from bitnob_utils.sms_utils import *
from bitnob_utils.funcs import *
from random import randint
from twilio.rest import TwilioRestClient
from django_twilio.utils import discover_twilio_credentials


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

    send_verification_sms:
    Send verification sms to user. Params should be phone

    verify_sms_code:
    Verify the sms code that was sent to the user's phone

    verify_inclusive:
    Endpoint to verify Ghanaian accounts

    verify_account:
    Verify Nigerian accounts using the bank account numbers using this URL


    """
    model = User
    permission_classes = [IsAuthenticated]
    serializer_class = UserModelSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @list_route(methods=['POST', 'PUT'])
    def uploads(self, request):
        return upload_files(request.data['file'])

    @detail_route(methods=['[POST', 'GET', 'PUT'])
    def send_verification_sms(self, request, pk=None):
        """
        Send Verification SMS to the user's phone
        """
        user = User.objects.get(pk=pk)
        send = send_code(request.data['phone'], user.country.iso_code)
        if send:
            return Response({"success": "SMS code succesfully sent"},  status=status.HTTP_200_OK)
        else:
            return Response({"error": "There was an error sending the code"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['[POST', 'GET', 'PUT'])
    def verify_sms_code(self, request, pk=None):
        """
         Verify SMS code that was sent
        """
        user = User.objects.get(pk=pk)
        verify = confirm_code(request.data['phone'], user.country.iso_code, request.data['code'])
        if verify:
            user.verified_phone = True
            user.phone = request.data['phone']
            user.save()
            return Response(data={
                "message": "Confirmed Phone Number Successfully",
                "status": 200}, status=status.HTTP_200_OK)
        else:
            return Response(data={
                "message": "Invalid SMS code, enter the correct value please"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['[POST', 'GET', 'PUT'])
    def add_phone_number(self, request, pk=None):
        """
         Verify SMS code that was sent
        """
        user = User.objects.get(pk=pk)
        user.phone = request.data['phone']
        user.verified_phone = True
        user.save()
        return Response(data={
            "message": "Added Phone Number Successfully",
            "status": 200}, status=status.HTTP_200_OK)

    @detail_route(methods=['PUT'])
    def verify_account(self, request, pk=None):
        """
        Verify user using BVN. This only works for Nigerian accounts
        :param request:
        :return: Response
        """
        user = User.objects.get(pk=pk)
        dob = request.data['dob']
        bvn = request.data['bvn']
        phone = request.data['phone']
        verified = bvn_verification(user, bvn, phone, dob)
        if verified:
            user.verification_completed = True
            user.phone = '0' + str(phone)
            user.save()
            return Response(data={"message": "Confirmed Account Successfully", "status": 200})
        else:
            return Response(data={"message": "Verification Failed, check the details you entered again"}, status=status.HTTP_400_BAD_REQUEST)

    @detail_route(methods=['PUT'])
    def verify_inclusive(self, request, pk=None):
        """
        verify Ghanaian accounts using this endpoint
        :param request:
        :return: `Response Json`
        """
        instance = self.get_object()
        verification_name = []
        id_number = request.data['id_number']
        fullname = " {} {}".format(request.user.first_name, request.user.last_name)
        fullname = transform_name(fullname)
        if request.data['method'] == 'Passport':
            verification_name = inclusive_passport(id_number)
        if request.data['method'] == 'SSNIT':
            verification_name = inclusive_ssnit(id_number)
        if request.data['method'] == 'Voters Card':
            verification_name = inclusive_voter_card(id_number)

        if not verification_name:
            return Response(data="This ID number is incorrect", status=status.HTTP_400_BAD_REQUEST)

        else:
            if is_similar(str(fullname), str(verification_name)):
                instance.verification_completed = True
                instance.save()
            else:
                return Response(
                    data="The information you provided does not match the information on the ID, "
                         "update your account name to match the on the ID",
                    status=status.HTTP_400_BAD_REQUEST)

        return Response(data="Successfully Verified Account", status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance.save()
        return Response(serializer.data)


class UserLoginHistoryModelViewSet(ModelViewSet):
    model = UserLoginHistory
    serializer_class = UserLoginHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserLoginHistory.objects.filter(user=self.request.user)


class AdminUserModelViewSet(ModelViewSet):
    """
    verified_users:
    Get all verified users

    unverified_users:
    Get unverified users

    verify_account:
    Admin should manually verify a user's account by passing the user's ID

    decline_verification:
    Decline a verification request

    make_admin:
    Make this account an admin account

    remove_admin:
    Degrade this account to a normal account

    """
    model = User
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserModelSerializer

    @detail_route(methods=['POST'], serializer_class=AdminUserModelSerializer)
    def make_admin(self, request, pk=None):
        user = User.objects.get(pk=pk)
        user.is_superuser = True
        user.save()
        return Response({"success": "Account Succesfully upgraded to admin"})

    @detail_route(methods=['POST'], serializer_class=AdminUserModelSerializer)
    def make_staff(self, request, pk=None):
        user = User.objects.get(pk=pk)
        user.is_staff = True
        user.save()
        return Response({"success": "Account Succesfully upgraded to staff"})

    @detail_route(methods=['POST'], serializer_class=AdminUserModelSerializer)
    def remove_staff(self, request, pk=None):
        user = User.objects.get(pk=pk)
        user.is_staff = False
        user.save()
        return Response({"success": "Account Succesfully removed from staff"})

    @detail_route(methods=['POST'], serializer_class=AdminUserModelSerializer)
    def remove_admin(self, request, pk=None):
        user = User.objects.get(pk=pk)
        user.is_superuser = False
        user.is_staff = False
        user.save()
        return Response({"success": "Account Succesfully degraded from admin"})

    @detail_route(methods=['POST'], serializer_class=AdminUserModelSerializer)
    def ban_account(self, request, pk=None):
        """
        Ban this account. This prevents the account from having access to the platform
        :param request:
        :param pk:
        :return:
        """
        user = User.objects.get(pk=pk)
        user.is_active = False
        user.save()
        return Response({"success": "Account Succesfully Banned"})

    @detail_route(methods=['POST'], serializer_class=AdminUserModelSerializer)
    def restore_banned_account(self, request, pk=None):
        """
        Restore this account
        :param request:
        :param pk:
        :return:
        """
        user = User.objects.get(pk=pk)
        user.is_active = True
        user.save()
        return Response({"success": "Banned Account Successfully Restored"})

    @list_route(methods=['GET'], serializer_class=AdminUserModelSerializer)
    def verified_users(self, request):
        """ Get all verified accounts """
        verified_users = User.objects.filter(verification_completed=True)
        serializer = self.get_serializer(verified_users, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET'], serializer_class=AdminUserModelSerializer)
    def unverified_users(self, request):
        """ Get all verified accounts """
        unverified_users = User.objects.filter(verification_completed=False)
        serializer = self.get_serializer(unverified_users, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET'], serializer_class=AdminUserModelSerializer)
    def banned_accounts(self, request):
        """ Get all banned accounts """
        banned_accounts = User.objects.filter(is_active=False)
        serializer = self.get_serializer(banned_accounts, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET'], serializer_class=AdminUserModelSerializer)
    def verification_requests(self, request, *args, **kwargs):
        """ Get all all accounts that have sent verification requests """
        verification_requests = User.objects.filter(verification_in_progress=True)
        serializer = self.get_serializer(verification_requests, many=True)
        return Response(serializer.data)

    @list_route(methods=['GET'], serializer_class=AdminUserModelSerializer)
    def declined_requests(self, request, *args, **kwargs):
        """ Get all all accounts that have been denied verification """
        verification_requests = User.objects.filter(verification_in_progress=True)
        serializer = self.get_serializer(verification_requests, many=True)
        return Response(serializer.data)

    @detail_route(methods=['POST', 'PUT'], serializer_class=AdminUserModelSerializer)
    def verify_account(self, request, pk=None):
        user = User.objects.get(pk=pk)
        user.verification_completed = True
        user.verification_in_progress = False
        serializer = self.get_serializer(user)
        user.save()
        return Response(serializer.data)

    @detail_route(methods=['POST', 'PUT'], serializer_class=AdminUserModelSerializer)
    def decline_verification(self, request, pk=None):
        user = User.objects.get(pk=pk)
        user.verification_in_progress = False
        serializer = self.get_serializer(user)
        user.save()
        return Response(serializer.data)


class UserStatsModelViewSet(ReadOnlyModelViewSet):
    model = User
    queryset = User.objects.all()
    serializer_class = AdminUserModelSerializer
    permission_classes = [IsAuthenticated]


    """
    user_stats:
    Statistics showing summary of user data on Bitnob
    
    """

    @list_route(methods=['GET'])
    def user_stats(self, request):
        user_total = User.objects.filter(is_superuser=False).count()
        active_users = User.objects.filter(is_active=True).count()
        return Response({
            "user_total": user_total,
            "active_users": active_users
        }, status=status.HTTP_200_OK)


