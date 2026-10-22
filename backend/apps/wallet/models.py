"""
wallet app – Payment integrations and transaction ledger.
"""
import uuid
from django.db import models
from django.conf import settings


class Transaction(models.Model):
    class TxnType(models.TextChoices):
        CREDIT = 'CREDIT', 'Credit'
        DEBIT = 'DEBIT', 'Debit'

    class TxnStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        SUCCESS = 'SUCCESS', 'Success'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions',
    )
    pickup = models.ForeignKey(
        'pickups.PickupRequest',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions',
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    txn_type = models.CharField(max_length=10, choices=TxnType.choices)
    status = models.CharField(max_length=10, choices=TxnStatus.choices, default=TxnStatus.PENDING)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                fields=['user', 'status'],
                name='wallet_txn_user_status_idx',
            ),
            models.Index(
                fields=['reference'],
                name='wallet_txn_reference_idx',
            ),
        ]

    def __str__(self):
        return f"{self.txn_type} ₹{self.amount} – {self.user.phone_number}"
