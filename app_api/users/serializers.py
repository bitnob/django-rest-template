from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer

from .models import User, UserLoginHistory, UserData
from wallet.serializers import UserWalletModelSerializer, WalletModelSerializer
from country.serializers import PublicCountryModelSerializer
from level.serializers import LevelModelSerializer, PublicLevelModelSerializer
from django.contrib.auth import get_user_model


User = get_user_model()


class UserLoginHistorySerializer(ModelSerializer):
    class Meta:
        model = UserLoginHistory
        fields = ['user', 'ip', 'browser', 'time']


class UserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        user_login = UserLoginHistorySerializer(many=True, read_only=True)
        user_wallet = UserWalletModelSerializer(read_only=True)
        country = PublicCountryModelSerializer(read_only=True, source='country')
        level = LevelModelSerializer(read_only=True, many=True)
        depth = 1
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'phone',
            'date_joined',
            'last_login',
        ]
        read_only_fields = (
            'id',

        )


class UsersModelSerializer(HyperlinkedModelSerializer):
    class Meta:
        model = User


class VerifyEmailSerializer(serializers.Serializer):
    key = serializers.CharField()
