"""
pickups app – Request lifecycle, geo-assignment logic.
"""
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import models


class PickupRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED = 'REQUESTED', 'Requested'
        ASSIGNED = 'ASSIGNED', 'Assigned'
        ON_THE_WAY = 'ON_THE_WAY', 'On The Way'
        ARRIVED = 'ARRIVED', 'Arrived'
        WEIGHING = 'WEIGHING', 'Weighing'
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
    estimated_payout = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_payout = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    notes = models.TextField(blank=True)
    cancellation_reason = models.CharField(max_length=255, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    arrived_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_time']),
        ]

    def __str__(self):
        return f"Pickup {self.id} – {self.status}"

    @property
    def is_active(self):
        return self.status in {
            self.Status.REQUESTED,
            self.Status.ASSIGNED,
            self.Status.ON_THE_WAY,
            self.Status.ARRIVED,
            self.Status.WEIGHING,
        }


class PickupItem(models.Model):
    """Line items within a pickup – estimated vs actual weights."""
    pickup = models.ForeignKey(PickupRequest, on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey('catalog.ScrapCategory', on_delete=models.PROTECT)
    estimated_weight_kg = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('0.000'))
    actual_weight_kg = models.DecimalField(max_digits=8, decimal_places=3, default=Decimal('0.000'))
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    calculated_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('pickup', 'category')

    def save(self, *args, **kwargs):
        if not self.unit_price and self.category_id:
            self.unit_price = self.category.base_price_per_kg
        weight = self.actual_weight_kg if self.actual_weight_kg else self.estimated_weight_kg
        self.calculated_price = (weight * self.unit_price).quantize(Decimal('0.01'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.category.name} – {self.actual_weight_kg or self.estimated_weight_kg}kg"


class PickupEvent(models.Model):
    """Audit trail for every status change on a pickup."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pickup = models.ForeignKey(PickupRequest, on_delete=models.CASCADE, related_name='events')
    from_status = models.CharField(max_length=20, blank=True)
    to_status = models.CharField(max_length=20)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pickup_events',
    )
    note = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.pickup_id}: {self.from_status} → {self.to_status}"
