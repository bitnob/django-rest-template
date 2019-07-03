from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import (ModelSerializer,
                                         HyperlinkedModelSerializer, SerializerMethodField
                                        )
from .models import Level, LevelUpgradeRequest


class PublicLevelModelSerializer(ModelSerializer):
    class Meta:
        model = Level
        fields = ['id',
                  'name',
                  'discount',
                  'max_limit',
                  'daily_limit',
                  'monthly_limit']


class LevelModelSerializer(ModelSerializer):
    class Meta:
        model = Level
        fields = ['id',
                  'name',
                  'discount',
                  'max_limit',
                  'daily_limit',
                  'monthly_limit']


class LevelUpgradeModelSerializer(ModelSerializer):
    class Meta:
        model = LevelUpgradeRequest
        fields = ['id',
                  'user',
                  'approved_by',
                  'approved',
                  'created',
                  'modified']


class AdminLevelModelSerializer(ModelSerializer):
    class Meta:
        model = Level
        fields = ['id',
                  'name',
                  'discount',
                  'max_limit',
                  'ng_limit',
                  'gh_limit',
                  'daily_limit',
                  'monthly_limit']


class AdminLevelUpgradeModelSerializer(ModelSerializer):

    class Meta:
        depth = 1
        model = LevelUpgradeRequest
        fields = ['id',
                  'user',
                  'level',
                  'address',
                  'declined',
                  'utility_bill',
                  'social_account',
                  'bvn',
                  'govt_id',
                  'selfie',
                  'approved_by',
                  'approved',
                  'created',
                  'modified']


