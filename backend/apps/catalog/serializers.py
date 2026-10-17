from rest_framework import serializers
from .models import ScrapCategory


class ScrapCategorySerializer(serializers.ModelSerializer):
    accepted_items_list = serializers.ListField(
        child=serializers.CharField(), read_only=True, source='accepted_items_list'
    )

    class Meta:
        model = ScrapCategory
        fields = [
            'id', 'name', 'description', 'accepted_items_list',
            'base_price_per_kg', 'unit', 'icon', 'sort_order', 'is_active',
        ]
