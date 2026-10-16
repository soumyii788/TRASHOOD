from django.contrib import admin
from .models import User, OTPVerification, CollectorProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'role', 'is_verified', 'is_active', 'created_at']
    list_filter = ['role', 'is_verified']
    search_fields = ['phone_number']


@admin.register(OTPVerification)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['user', 'otp_code', 'is_used', 'expires_at']


@admin.register(CollectorProfile)
class CollectorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'vehicle_type', 'kyc_status', 'is_available']
    list_filter = ['kyc_status', 'vehicle_type']
