from django.contrib import admin
from .models import CustomerProfile, Address


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'last_name', 'created_at']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['customer', 'label', 'city', 'state', 'is_default']
    list_filter = ['label', 'city']
