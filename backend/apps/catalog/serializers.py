from rest_framework import serializers
from .models import ScrapCategory


class ScrapCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ScrapCategory
        fields = ['id', 'name', 'base_price_per_kg', 'icon', 'is_active']
