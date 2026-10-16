"""
pickups app – Request lifecycle, geo-assignment logic.
"""
import uuid
from django.db import models
from django.conf import settings


class PickupRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        ON_THE_WAY = 'ON_THE_WAY', 'On The Way'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        'customers.CustomerProfile', on_delete=models.CASCADE, related_name='pickup_requests'
    )
    assigned_collector = models.ForeignKey(
        'accounts.CollectorProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_pickups',
    )
    pickup_address = models.ForeignKey(
        'customers.Address',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.REQUESTED)
    scheduled_time = models.DateTimeField()
    total_payout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Pickup {self.id} – {self.status}"


class PickupItem(models.Model):
    """Line items within a pickup – individual scrap categories + weights."""
    pickup = models.ForeignKey(PickupRequest, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey('catalog.ScrapCategory', on_delete=models.PROTECT)
    actual_weight_kg = models.DecimalField(max_digits=8, decimal_places=3, default=0.000)
    calculated_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        self.calculated_price = self.actual_weight_kg * self.category.base_price_per_kg
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} – {self.actual_weight_kg}kg"
