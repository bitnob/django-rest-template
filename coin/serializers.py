from rest_framework.serializers import ModelSerializer
from .models import Coin


class CoinModelSerializer(ModelSerializer):

    class Meta:
        model = Coin
        lookup_field = 'pk'
        fields = (
            'name',
            'symbol',
            'status',
            'logo',
            'slug',
            'id',
        )


class AdminCoinModelSerializer(ModelSerializer):
    class Meta:
        model = Coin
        lookup_field = 'pk'
        fields = (
            'name',
            'symbol',
            'buy_rate',
            'sell_rate',
            'purchase_price',
            'status',
            'fees',
            'logo',
            'slug',
            'id',
            'created',
            'modified'
        )
