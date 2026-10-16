"""
catalog app – Scrap categories and dynamic pricing matrix.
"""
import uuid
from django.db import models


class ScrapCategory(models.Model):
    """
    Represents a scrap type (e.g., Iron, Newspaper) with admin-controlled pricing.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    base_price_per_kg = models.DecimalField(max_digits=8, decimal_places=2)
    icon = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Scrap Category'
        verbose_name_plural = 'Scrap Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (₹{self.base_price_per_kg}/kg)"
