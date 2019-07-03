from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from .models import Stat
import requests
# import africastalking
from rest_framework.response import Response
from .serializers import StatModelSerializer
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from bitnob_api.users.models import User
from orders.models import BuyOrder
from bitnob_utils.stats_utils import *

# Initialize SDK
# username = "sandbox"   # use 'sandbox' for development in the test environment
# api_key = "908ac7fee51e02b930ed6d519001ac9149e98dafab2ef890ab12e38014f25ab5"
# africastalking.initialize(username, api_key)
#
# headers = {'Content-Type':  'text/plain'}
# sms = africastalking.SMS


class StatModelViewSet(ModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = StatModelSerializer
    model = Stat

    #908ac7fee51e02b930ed6d519001ac9149e98dafab2ef890ab12e38014f25ab5

    @csrf_exempt
    @list_route(methods=['POST'], permission_classes=[AllowAny])
    def ussd(self, request):
        print(request.data)
        if request.data['text'] == '':
            response = "CON this is working well"
            return response
            # return requests.post(data=response, headers=headers)

    @list_route(methods=['POST'])
    def sms(self, request):
        # Use the service synchronously
        response = sms.send("Hello Message!", ["+2348068476165"])
        print(response)

    @list_route(methods=['GET'])
    def user_stats(self, request):
        user_total = User.objects.filter(is_superuser=False).count()
        active_users = User.objects.filter(is_active=True).count()
        new_users_today = User.objects.filter(date_joined__gte=today).count()
        new_users_yesterday = User.objects.filter(date_joined__gte=yesterday).count()
        new_users_week = User.objects.filter(date_joined__gte=last_week).count()
        new_users_month = User.objects.filter(date_joined__gte=last_month).count()
        new_users_year = User.objects.filter(date_joined__gte=last_year).count()
        return Response({
            "user_total": user_total,
            "active_users": active_users,
            "new_users_today": new_users_today,
            "new_users_yesterday": new_users_yesterday,
            "new_users_lastweek": new_users_week,
            "new_users_last_month": new_users_month,
            "new_users_year": new_users_year,
        }, status=status.HTTP_200_OK)

    @list_route(methods=['GET'])
    def sales(self, request):
        return Response({
            'total_sales': 0
        })

    @list_route(methods=['GET'])
    def deposits_stats(self, request):
        return Response({
            'total_deposits': 0
        })



