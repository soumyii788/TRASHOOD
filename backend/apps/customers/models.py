"""
customers app – User profiles and geo-validated addresses.
"""
import uuid
from django.db import models
from django.conf import settings


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='customer_profile',
        limit_choices_to={'role': 'CUSTOMER'},
    )
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user.phone_number})"


class Address(models.Model):
    class Label(models.TextChoices):
        HOME = 'HOME', 'Home'
        OFFICE = 'OFFICE', 'Office'
        OTHER = 'OTHER', 'Other'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='addresses')
    label = models.CharField(max_length=10, choices=Label.choices, default=Label.HOME)
    address_line1 = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    long = models.DecimalField(max_digits=9, decimal_places=6)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.label} – {self.address_line1}, {self.city}"
