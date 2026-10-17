from django.contrib import admin
from .models import ScrapCategory


@admin.register(ScrapCategory)
class ScrapCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price_per_kg', 'unit', 'sort_order', 'is_active', 'updated_at']
    list_editable = ['base_price_per_kg', 'unit', 'sort_order', 'is_active']
    search_fields = ['name']
    fields = ['name', 'description', 'accepted_items', 'base_price_per_kg', 'unit', 'icon', 'sort_order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
