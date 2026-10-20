from rest_framework import serializers

from apps.catalog.models import ScrapCategory
from apps.customers.serializers import AddressSerializer

from .models import PickupRequest, PickupItem, PickupEvent


class PickupItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    unit = serializers.CharField(source='category.unit', read_only=True)

    class Meta:
        model = PickupItem
        fields = [
            'id', 'category', 'category_name', 'unit',
            'estimated_weight_kg', 'actual_weight_kg',
            'unit_price', 'calculated_price',
        ]
        read_only_fields = ['calculated_price', 'unit_price']


class PickupItemWriteSerializer(serializers.Serializer):
    category = serializers.UUIDField()
    estimated_weight_kg = serializers.DecimalField(
        max_digits=8, decimal_places=3, required=False, default=0
    )
    actual_weight_kg = serializers.DecimalField(
        max_digits=8, decimal_places=3, required=False
    )

    def validate_category(self, value):
        if not ScrapCategory.objects.filter(pk=value, is_active=True).exists():
            raise serializers.ValidationError('Category not found or inactive.')
        return value


class PickupEventSerializer(serializers.ModelSerializer):
    actor_phone = serializers.CharField(source='actor.phone_number', read_only=True)

    class Meta:
        model = PickupEvent
        fields = ['id', 'from_status', 'to_status', 'actor_phone', 'note', 'created_at']


class PickupRequestSerializer(serializers.ModelSerializer):
    items = PickupItemSerializer(many=True, read_only=True)
    events = PickupEventSerializer(many=True, read_only=True)
    pickup_address_detail = AddressSerializer(source='pickup_address', read_only=True)
    assigned_collector_detail = serializers.SerializerMethodField()
    distance_km = serializers.SerializerMethodField()

    class Meta:
        model = PickupRequest
        fields = [
            'id', 'customer', 'assigned_collector', 'assigned_collector_detail',
            'pickup_address', 'pickup_address_detail',
            'status', 'scheduled_time', 'estimated_payout', 'total_payout',
            'notes', 'cancellation_reason',
            'assigned_at', 'started_at', 'arrived_at', 'completed_at', 'cancelled_at',
            'items', 'events', 'distance_km', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'customer', 'assigned_collector', 'status',
            'estimated_payout', 'total_payout', 'cancellation_reason',
            'assigned_at', 'started_at', 'arrived_at', 'completed_at', 'cancelled_at',
            'created_at', 'updated_at',
        ]

    def get_assigned_collector_detail(self, obj):
        collector = obj.assigned_collector
        if not collector:
            return None
        return {
            'id': collector.id,
            'vehicle_type': collector.vehicle_type,
            'current_lat': collector.current_lat,
            'current_long': collector.current_long,
        }

    def get_distance_km(self, obj):
        return getattr(obj, 'distance_km', None)


class CreatePickupSerializer(serializers.ModelSerializer):
    items = PickupItemWriteSerializer(many=True, required=False)

    class Meta:
        model = PickupRequest
        fields = ['pickup_address', 'scheduled_time', 'notes', 'items']

    def validate_pickup_address(self, value):
        request = self.context.get('request')
        if request and value:
            profile = getattr(request.user, 'customer_profile', None)
            if profile and value.customer_id != profile.id:
                raise serializers.ValidationError('Address does not belong to this customer.')
        return value

    def validate_scheduled_time(self, value):
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError('Scheduled time must be in the future.')
        return value


class CancelPickupSerializer(serializers.Serializer):
    reason = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')


class JobStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=PickupRequest.Status.choices,
        required=False,
    )
    note = serializers.CharField(max_length=255, required=False, allow_blank=True, default='')


class WeighItemsSerializer(serializers.Serializer):
    items = PickupItemWriteSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError('At least one item is required.')
        for row in value:
            if row.get('actual_weight_kg') is None:
                raise serializers.ValidationError('actual_weight_kg is required for each item.')
        return value
