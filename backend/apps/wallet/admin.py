from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'txn_type', 'status', 'pickup', 'created_at']
    list_filter = ['txn_type', 'status']
    search_fields = ['user__phone_number', 'reference']
    readonly_fields = ['id', 'created_at']
