from rest_framework import serializers
from rest_framework.serializers import (
    ModelSerializer,
)
from .models import Country


class PublicCountryModelSerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'iso_code', 'tel_code', 'currency']


class AdminCountryModelSerializer(ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'iso_code', 'tel_code', 'currency', 'active', 'created', 'modified']


