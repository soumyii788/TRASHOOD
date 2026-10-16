from django.contrib import admin
from .models import ScrapCategory


@admin.register(ScrapCategory)
class ScrapCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'base_price_per_kg', 'is_active', 'updated_at']
    list_editable = ['base_price_per_kg', 'is_active']
    search_fields = ['name']
