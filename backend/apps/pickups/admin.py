from django.contrib import admin
from .models import PickupRequest, PickupItem, PickupEvent


class PickupItemInline(admin.TabularInline):
    model = PickupItem
    extra = 0


class PickupEventInline(admin.TabularInline):
    model = PickupEvent
    extra = 0
    readonly_fields = ['from_status', 'to_status', 'actor', 'note', 'created_at']
    can_delete = False


@admin.register(PickupRequest)
class PickupRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'assigned_collector', 'status', 'scheduled_time', 'estimated_payout', 'total_payout']
    list_filter = ['status']
    search_fields = ['id', 'customer__user__phone_number']
    inlines = [PickupItemInline, PickupEventInline]
