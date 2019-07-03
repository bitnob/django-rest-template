"""
Set of serializers that will hide some important fields
"""

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, HyperlinkedModelSerializer
from bitnob_api.users.models import User
from level.models import Level, LevelUpgradeRequest


class LevelModelSerializer(ModelSerializer):
    class Meta:
        fields = ['']
