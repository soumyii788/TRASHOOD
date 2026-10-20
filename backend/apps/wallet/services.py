"""Wallet settlement for completed pickups."""
from decimal import Decimal

from django.conf import settings
from django.db import transaction

from .models import Transaction


def _commission_rate():
    return Decimal(str(getattr(settings, 'COLLECTOR_COMMISSION_RATE', '0.10')))


def _already_settled(user, pickup, reference):
    return Transaction.objects.filter(
        user=user,
        pickup=pickup,
        reference=reference,
        status=Transaction.TxnStatus.SUCCESS,
    ).exists()


@transaction.atomic
def settle_pickup(pickup):
    """
    Credit the customer the scrap payout and the collector a commission.
    Idempotent: repeating this for the same pickup will not double-pay.
    """
    amount = Decimal(pickup.total_payout or 0)
    if amount <= 0:
        return []

    created = []
    customer_user = pickup.customer.user
    customer_ref = f'pickup:{pickup.id}:customer_payout'
    if not _already_settled(customer_user, pickup, customer_ref):
        created.append(Transaction.objects.create(
            user=customer_user,
            pickup=pickup,
            amount=amount,
            txn_type=Transaction.TxnType.CREDIT,
            status=Transaction.TxnStatus.SUCCESS,
            reference=customer_ref,
        ))

    collector = pickup.assigned_collector
    if collector:
        fee = (amount * _commission_rate()).quantize(Decimal('0.01'))
        collector_ref = f'pickup:{pickup.id}:collector_fee'
        if fee > 0 and not _already_settled(collector.user, pickup, collector_ref):
            created.append(Transaction.objects.create(
                user=collector.user,
                pickup=pickup,
                amount=fee,
                txn_type=Transaction.TxnType.CREDIT,
                status=Transaction.TxnStatus.SUCCESS,
                reference=collector_ref,
            ))

    return created
