from rest_framework import serializers
from .models import CustomerProfile, Address


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'label', 'address_line1', 'city', 'state', 'zip_code', 'lat', 'long', 'is_default']
        read_only_fields = ['id']


class CustomerProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)

    class Meta:
        model = CustomerProfile
        fields = ['first_name', 'last_name', 'avatar', 'addresses']
