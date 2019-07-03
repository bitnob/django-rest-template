from rest_framework.serializers import ModelSerializer
from .models import Stat


class StatModelSerializer(ModelSerializer):
    class Meta:
        model = Stat
        fields = []
