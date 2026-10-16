from rest_framework import serializers
from .models import PickupRequest, PickupItem


class PickupItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = PickupItem
        fields = ['id', 'category', 'category_name', 'actual_weight_kg', 'calculated_price']
        read_only_fields = ['calculated_price']


class PickupRequestSerializer(serializers.ModelSerializer):
    items = PickupItemSerializer(many=True, read_only=True)

    class Meta:
        model = PickupRequest
        fields = [
            'id', 'customer', 'assigned_collector', 'pickup_address',
            'status', 'scheduled_time', 'total_payout', 'notes', 'items', 'created_at',
        ]
        read_only_fields = ['id', 'customer', 'assigned_collector', 'status', 'total_payout', 'created_at']


class CreatePickupSerializer(serializers.ModelSerializer):
    class Meta:
        model = PickupRequest
        fields = ['pickup_address', 'scheduled_time', 'notes']
