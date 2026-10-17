"""
catalog app – Scrap categories and dynamic pricing matrix.
"""
import uuid
from django.db import models


class ScrapCategory(models.Model):
    """
    Represents a scrap type (e.g., Iron, Newspaper) with admin-controlled pricing.
    All pricing and content fields are set via Django admin – nothing is hardcoded in frontend.
    """

    class Unit(models.TextChoices):
        KG = 'kg', 'per kg'
        UNIT = 'unit', 'per unit'
        LITRE = 'litre', 'per litre'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(
        blank=True,
        help_text="Short description shown in the catalog (e.g. 'Old newspapers, magazines, cardboard').",
    )
    accepted_items = models.TextField(
        blank=True,
        help_text="Comma-separated accepted items shown as rules on the UI.",
    )
    base_price_per_kg = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text="Indicative buyback price per unit. Actual payout may vary by condition.",
    )
    unit = models.CharField(
        max_length=10,
        choices=Unit.choices,
        default=Unit.KG,
        help_text="Measurement unit for pricing (kg, unit, litre).",
    )
    icon = models.URLField(blank=True, null=True, help_text="Optional hosted image URL for this category.")
    sort_order = models.PositiveSmallIntegerField(
        default=0,
        help_text="Lower numbers appear first in the catalog.",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Scrap Category'
        verbose_name_plural = 'Scrap Categories'
        ordering = ['sort_order', 'name']

    def __str__(self):
        return f"{self.name} (₹{self.base_price_per_kg}/{self.unit})"

    @property
    def accepted_items_list(self):
        """Returns accepted_items as a cleaned list."""
        return [i.strip() for i in self.accepted_items.split(',') if i.strip()]
