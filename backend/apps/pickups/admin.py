from django.contrib import admin
from .models import PickupRequest, PickupItem


class PickupItemInline(admin.TabularInline):
    model = PickupItem
    extra = 0


@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'assigned_collector', 'status', 'scheduled_time', 'total_payout']
    list_filter = ['status']
    inlines = [PickupItemInline]
