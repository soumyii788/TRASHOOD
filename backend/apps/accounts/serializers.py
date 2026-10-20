"""
Serializers for accounts app – OTP flow and collector profile.
"""
from rest_framework import serializers
from .models import User, CollectorProfile


class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    role = serializers.ChoiceField(choices=['CUSTOMER', 'COLLECTOR'], default='CUSTOMER')


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp_code = serializers.CharField(max_length=6)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'role', 'is_verified', 'created_at']
        read_only_fields = ['id', 'is_verified', 'created_at']


class CollectorProfileSerializer(serializers.ModelSerializer):
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)

    class Meta:
        model = CollectorProfile
        fields = [
            'id', 'phone_number', 'vehicle_type', 'kyc_status', 'is_available',
            'current_lat', 'current_long', 'last_location_at',
        ]
        read_only_fields = ['id', 'kyc_status', 'current_lat', 'current_long', 'last_location_at']


class CollectorLocationSerializer(serializers.Serializer):
    lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    long = serializers.DecimalField(max_digits=9, decimal_places=6)


class AvailabilitySerializer(serializers.Serializer):
    is_available = serializers.BooleanField()
