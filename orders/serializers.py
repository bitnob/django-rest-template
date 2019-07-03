from rest_framework.serializers import (
    ModelSerializer,
    CurrentUserDefault,
    PrimaryKeyRelatedField,
)
from rest_framework import serializers
from .models import BuyOrder, SellOrder, Invoice


class InvoiceModelSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())

    class Meta:
        model = Invoice
        lookup_field = 'pk'
        fields = (
                  'id',
                  'user',
                  'wallet_address',
                  'amount',
                  'btc_amount',
                  'local_value',
                  'expiry',
                  'fees',
                  'status',
                  'reference_id',
                  'created',
                  )
        read_only_fields = ('id',)


class BuyOrderModelSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())
    coin_name = serializers.ReadOnlyField(source='coin.name')

    class Meta:
        model = BuyOrder
        lookup_field = 'pk'
        fields = (
                  'id',
                  'user',
                  'address',
                  'amount',
                  'cost',
                  'fee',
                  'coin',
                  'coin_name',
                  'reference_id',
                  'transaction_id',
                  'created',
                  )
        read_only_fields = ('id',)


class SellOrderModelSerializer(ModelSerializer):
    user = PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())
    coin_name = serializers.ReadOnlyField(source='coin.name')

    class Meta:
        model = SellOrder
        lookup_field = 'pk'
        fields = (
                  'id',
                  'user',
                  'address',
                  'amount_sold',
                  'cost',
                  'fee',
                  'coin',
                  'coin_name',
                  'reference_id',
                  'transaction_id',
                  'created',
                  )
        read_only_fields = ('id',)

