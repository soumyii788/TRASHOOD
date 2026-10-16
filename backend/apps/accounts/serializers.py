"""
Serializers for accounts app – OTP flow and collector profile.
"""
from rest_framework import serializers
from django.utils import timezone
from datetime import timedelta
from .models import User, OTPVerification, CollectorProfile


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
    class Meta:
        model = CollectorProfile
        fields = ['vehicle_type', 'kyc_status', 'is_available', 'current_lat', 'current_long']
        read_only_fields = ['kyc_status']


class CollectorLocationSerializer(serializers.Serializer):
    lat = serializers.DecimalField(max_digits=9, decimal_places=6)
    long = serializers.DecimalField(max_digits=9, decimal_places=6)
