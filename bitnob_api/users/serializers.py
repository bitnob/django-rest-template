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


class UserDataModelSerializer(ModelSerializer):
    class Meta:
        model = UserData
        fields = ['user', 'address', 'utility_bill', 'social_account', 'bvn', 'govt_id', 'selfie']


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
            'country',
            'referral_code',
            'verified_phone',
            'verification_in_progress',
            'verification_completed',
            'user_login',
            'user_wallet',
            'level',
            'phone',
            'date_joined',
            'last_login',
        ]
        read_only_fields = (
            'id',

        )


class AdminUserModelSerializer(ModelSerializer):
    class Meta:
        model = User
        user_kyc = UserDataModelSerializer(read_only=True)
        user_login = UserLoginHistorySerializer(many=True, read_only=True)
        user_wallet = WalletModelSerializer(read_only=True)
        country = PublicCountryModelSerializer(read_only=True)
        level = LevelModelSerializer(read_only=True, many=True, source='level')
        depth = 1
        fields = [
            'id',
            'username',
            'email',
            'verification_in_progress',
            'verification_completed',
            'user_wallet',
            'user_kyc',
            'country',
            'is_staff',
            'level',
            'user_login',
            'is_superuser',
            'is_active',
            'phone',
            'address',
            'date_joined',
            'first_name',
            'last_name',
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
