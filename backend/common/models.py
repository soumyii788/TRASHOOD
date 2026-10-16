"""
Common abstract base models and shared utilities used across all apps.
"""
import uuid
from django.db import models


class TimeStampedModel(models.Model):
    """
    Abstract base model that provides self-updating
    `created_at` and `updated_at` fields.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UUIDModel(models.Model):
    """
    Abstract base model that uses UUID as the primary key.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class BaseModel(UUIDModel, TimeStampedModel):
    """
    Convenience mixin combining UUID PK + timestamps.
    Inherit from this for all core business models.
    """
    class Meta:
        abstract = True
