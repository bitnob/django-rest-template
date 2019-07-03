from django.core.serializers import json
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
import json
from rest_framework import serializers
from bitnob_api.users.models import User, UserData
from bitnob_api.users.serializers import AdminUserModelSerializer
from .models import Level, LevelUpgradeRequest
from .serializers import (LevelModelSerializer,
                          AdminLevelModelSerializer,
                          AdminLevelUpgradeModelSerializer,
                          LevelUpgradeModelSerializer)
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.decorators import list_route, detail_route


class LevelModelViewSet(ReadOnlyModelViewSet):
    """
    List all Levels
    """
    model = Level
    serializer_class = LevelModelSerializer
    permission_classes = [AllowAny]
    queryset = Level.objects.all()


class LevelUpgradeRequestModelViewSet(ModelViewSet):
    """
    Request change of level upgrade
    """
    model = Level
    serializer_class = LevelUpgradeModelSerializer
    permission_classes = [IsAuthenticated]
    model = LevelUpgradeRequest

    def get_queryset(self, request):
        return LevelUpgradeRequest.objects.filter(user=request.user.id)

    @list_route(methods=['POST', 'PUT'])
    def level_two_upgrade(self, request):
        user = User.objects.get(id=request.user.id)
        user.verification_in_progress = True
        UserData.objects.create(user=user,
                                govt_id=request.data['file'],
                                social_account=request.data['social_account'],
                                address=request.data['address'])
        LevelUpgradeRequest.objects.create(user=user, govt_id=request.data['file'],
                                           social_account=request.data['social_account'],
                                           address=request.data['address'])
        user.save()
        return Response({"message": "Request was successfully submitted"}, status=status.HTTP_201_CREATED)

    @list_route(methods=['POST', 'PUT'])
    def level_three_upgrade(self, request):
        user = User.objects.get(id=request.user.id)
        user_kyc_data = UserData.objects.get(user=user.id)
        user_kyc_data(utility_bill=request.data['file'])
        user_kyc_data.save()
        # UserData.objects.create(user=user,
        #                         utility_bill=request.data['file'])
        LevelUpgradeRequest.objects.create(user=user)
        user.save()
        return Response({"message": "Request was successfully submitted"}, status=status.HTTP_201_CREATED)


class AdminLevelModelViewSet(ModelViewSet):
    """
    Endpoints for admin to manage levels

    level_one_accounts:
    (GET)List all users on level one

    level_two_accounts:
    list all users on level 2

    level_three_accounts:
    list all users on level 3

    level_four_accounts:
   h  List all users on level 4
    """
    model = Level
    serializer_class = AdminLevelModelSerializer
    permission_classes = [IsAuthenticated]
    queryset = Level.objects.all()


class AdminLevelUpgradeRequestModelViewSet(ModelViewSet):
    serializer_class = AdminLevelUpgradeModelSerializer
    permission_classes = [IsAdminUser]
    model = Level
    queryset = LevelUpgradeRequest.objects.all()

    """
     approve_upgrade: Approve an upgrade request. 
     id - Id of the Upgrade Request
     user_id
     
     
    """

    def get_queryset(self):
        return LevelUpgradeRequest.objects.filter(approved=False)

    def get_level(self, name):
        """
        get level
        :return: <Object Level>
        """
        return Level.objects.get(name=name)

    def get_user(self, user_id):
        """
        :param request:
        :return: <Object User>
        """
        return User.objects.get(id=user_id)

    def get_upgrade_request(self, id):
        return LevelUpgradeRequest.objects.get(id=id)

    @list_route(methods=['POST'])
    def approve(self, request):
        """
        :param id:
        :param user_id:
        :return:
        """
        user = self.get_user(request.data['user_id'])
        upgrade_req = self.get_upgrade_request(request.data['id'])
        if user.level.name == 'Level 1':
            user.level = self.get_level("Level 2")
            user.save()
            upgrade_req.approved = True
            upgrade_req.save()
        if user.level.name == 'Level 2':
            user.level = self.get_level("Level 3")
            user.save()
            upgrade_req.approved = True
            upgrade_req.save()
        if user.level.name == 'Level 3':
            user.level = self.get_level("Level 4")
            user.save()
            upgrade_req.approved = True
            upgrade_req.save()
        else:
            return Response({"message": "This account is already on the highest level"})
        return Response({"message": "Successfully Upgraded account"})

    @list_route(methods=['POST'])
    def decline(self, request):
        """
        :param id:
        :param user_id:
        :return:
        """
        print(request.data)
        user = self.get_user(request.data['user_id'])
        upgrade_req = self.get_upgrade_request(request.data['id'])
        upgrade_req.declined = True
        upgrade_req.save()
        return Response({"message": "Successfully Declined Request"})

    @list_route(methods=['POST'])
    def specific_upgrade(self, request):
        user = self.get_user(request)
        level = Level.objects.get(request.data['level_id'])
        user.level = level
        user.save()
        return Response({"message": "Successfully Changed Account Level"})

    @list_route(methods=['GET'])
    def declined(self, request):
        declined = LevelUpgradeRequest.objects.filter(declined=True)
        return Response({"data": declined})

    @list_route(methods=['GET'])
    def approved(self, request):
        approved = LevelUpgradeRequest.objects.filter(approved=True)
        return Response({"data": approved})



class UpgradeLevelRequestModelViewSet(ModelViewSet):
    """ All Requests to upgrade accounts """
    model = LevelUpgradeRequest
    serializer_class = AdminLevelModelSerializer
    authentication_classes = [AllowAny]
    permission_classes = [AllowAny]
    queryset = LevelUpgradeRequest.objects.all()












