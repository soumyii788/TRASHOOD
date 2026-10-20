"""
Pickup pipeline: status machine, assignment, weighing, completion, cancel.
"""
from decimal import Decimal

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from apps.catalog.models import ScrapCategory
from apps.wallet.services import settle_pickup
from common.geo import haversine_km, as_decimal_km

from .models import PickupRequest, PickupItem, PickupEvent


# Allowed next statuses from a given current status.
TRANSITIONS = {
    PickupRequest.Status.REQUESTED: {
        PickupRequest.Status.ASSIGNED,
        PickupRequest.Status.CANCELLED,
    },
    PickupRequest.Status.ASSIGNED: {
        PickupRequest.Status.ON_THE_WAY,
        PickupRequest.Status.CANCELLED,
    },
    PickupRequest.Status.ON_THE_WAY: {
        PickupRequest.Status.ARRIVED,
        PickupRequest.Status.COMPLETED,  # legacy one-step complete
        PickupRequest.Status.CANCELLED,
    },
    PickupRequest.Status.ARRIVED: {
        PickupRequest.Status.WEIGHING,
        PickupRequest.Status.COMPLETED,
        PickupRequest.Status.CANCELLED,
    },
    PickupRequest.Status.WEIGHING: {
        PickupRequest.Status.COMPLETED,
        PickupRequest.Status.CANCELLED,
    },
}

CUSTOMER_CANCELLABLE = {
    PickupRequest.Status.REQUESTED,
    PickupRequest.Status.ASSIGNED,
}

COLLECTOR_CANCELLABLE = {
    PickupRequest.Status.ASSIGNED,
    PickupRequest.Status.ON_THE_WAY,
}

FORWARD_DEFAULT = {
    PickupRequest.Status.ASSIGNED: PickupRequest.Status.ON_THE_WAY,
    PickupRequest.Status.ON_THE_WAY: PickupRequest.Status.ARRIVED,
    PickupRequest.Status.ARRIVED: PickupRequest.Status.WEIGHING,
    PickupRequest.Status.WEIGHING: PickupRequest.Status.COMPLETED,
}


def _notify(event, pickup):
    from apps.notifications.tasks import notify_pickup_event
    from common.tasks import enqueue
    enqueue(notify_pickup_event, str(pickup.id), event)


def _record_event(pickup, from_status, to_status, actor=None, note=''):
    PickupEvent.objects.create(
        pickup=pickup,
        from_status=from_status or '',
        to_status=to_status,
        actor=actor,
        note=note or '',
    )


def _line_price(weight, unit_price):
    return (Decimal(weight or 0) * Decimal(unit_price or 0)).quantize(Decimal('0.01'))


def recompute_payouts(pickup):
    """Refresh estimated and actual totals from line items."""
    estimated = Decimal('0.00')
    actual = Decimal('0.00')
    for item in pickup.items.all():
        estimated += _line_price(item.estimated_weight_kg, item.unit_price)
        if item.actual_weight_kg and item.actual_weight_kg > 0:
            actual += _line_price(item.actual_weight_kg, item.unit_price)
    pickup.estimated_payout = estimated
    if actual > 0:
        pickup.total_payout = actual
    pickup.save(update_fields=['estimated_payout', 'total_payout', 'updated_at'])
    return pickup


def upsert_items(pickup, items_data, *, use_actual=False):
    """
    items_data: iterable of dicts with category (id or instance),
    estimated_weight_kg and/or actual_weight_kg.
    """
    if not items_data:
        return

    for row in items_data:
        category = row.get('category')
        if isinstance(category, ScrapCategory):
            cat = category
        else:
            try:
                cat = ScrapCategory.objects.get(pk=category, is_active=True)
            except ScrapCategory.DoesNotExist as exc:
                raise ValidationError({'items': f'Unknown or inactive category: {category}'}) from exc

        item, _ = PickupItem.objects.get_or_create(
            pickup=pickup,
            category=cat,
            defaults={'unit_price': cat.base_price_per_kg},
        )
        if not item.unit_price:
            item.unit_price = cat.base_price_per_kg

        if 'estimated_weight_kg' in row and row['estimated_weight_kg'] is not None:
            item.estimated_weight_kg = Decimal(str(row['estimated_weight_kg']))
        if use_actual or row.get('actual_weight_kg') is not None:
            item.actual_weight_kg = Decimal(str(row.get('actual_weight_kg') or 0))

        weight_for_price = item.actual_weight_kg if item.actual_weight_kg else item.estimated_weight_kg
        item.calculated_price = _line_price(weight_for_price, item.unit_price)
        item.save()

    recompute_payouts(pickup)


@transaction.atomic
def create_pickup(*, customer, pickup_address, scheduled_time, notes='', items=None):
    if pickup_address and pickup_address.customer_id != customer.id:
        raise ValidationError({'pickup_address': 'Address does not belong to this customer.'})

    pickup = PickupRequest.objects.create(
        customer=customer,
        pickup_address=pickup_address,
        scheduled_time=scheduled_time,
        notes=notes or '',
        status=PickupRequest.Status.REQUESTED,
    )
    if items:
        upsert_items(pickup, items, use_actual=False)
    _record_event(pickup, '', PickupRequest.Status.REQUESTED, actor=customer.user, note='Pickup requested')
    _notify('requested', pickup)
    return pickup


def nearby_jobs(*, collector, radius_km=15, lat=None, lon=None):
    qs = PickupRequest.objects.filter(
        status=PickupRequest.Status.REQUESTED,
        assigned_collector__isnull=True,
    ).select_related('pickup_address', 'customer').prefetch_related('items__category')

    origin_lat = lat if lat not in (None, '') else collector.current_lat
    origin_lon = lon if lon not in (None, '') else collector.current_long
    try:
        radius = float(radius_km) if radius_km not in (None, '') else None
    except (TypeError, ValueError):
        radius = 15.0

    jobs = list(qs)
    annotated = []
    for job in jobs:
        addr = job.pickup_address
        distance = None
        if origin_lat is not None and origin_lon is not None and addr:
            distance = haversine_km(origin_lat, origin_lon, addr.lat, addr.long)
        if radius is not None and distance is not None and distance > radius:
            continue
        job.distance_km = as_decimal_km(distance)
        annotated.append(job)

    annotated.sort(key=lambda j: (j.distance_km is None, j.distance_km or 0, j.scheduled_time))
    return annotated


@transaction.atomic
def accept_job(*, pickup_id, collector):
    if collector.kyc_status == collector.KycStatus.REJECTED:
        raise PermissionDenied('Collector KYC has been rejected.')

    try:
        pickup = PickupRequest.objects.select_for_update().select_related(
            'customer__user', 'pickup_address'
        ).get(pk=pickup_id)
    except PickupRequest.DoesNotExist as exc:
        raise NotFound('Job not found.') from exc

    if pickup.status != PickupRequest.Status.REQUESTED or pickup.assigned_collector_id:
        raise ValidationError({'detail': 'Job is no longer available.'})

    prev = pickup.status
    pickup.assigned_collector = collector
    pickup.status = PickupRequest.Status.ASSIGNED
    pickup.assigned_at = timezone.now()
    pickup.save(update_fields=['assigned_collector', 'status', 'assigned_at', 'updated_at'])
    _record_event(pickup, prev, pickup.status, actor=collector.user, note='Collector accepted job')
    _notify('assigned', pickup)
    return pickup


@transaction.atomic
def transition(*, pickup, to_status, actor, note=''):
    if to_status not in TRANSITIONS.get(pickup.status, set()):
        raise ValidationError({
            'status': f'Cannot move from {pickup.status} to {to_status}.',
        })

    prev = pickup.status
    pickup.status = to_status
    now = timezone.now()
    extra = ['status', 'updated_at']

    if to_status == PickupRequest.Status.ON_THE_WAY and not pickup.started_at:
        pickup.started_at = now
        extra.append('started_at')
    if to_status == PickupRequest.Status.ARRIVED and not pickup.arrived_at:
        pickup.arrived_at = now
        extra.append('arrived_at')
    if to_status == PickupRequest.Status.COMPLETED:
        pickup.completed_at = now
        extra.append('completed_at')
    if to_status == PickupRequest.Status.CANCELLED:
        pickup.cancelled_at = now
        extra.append('cancelled_at')

    pickup.save(update_fields=extra)
    _record_event(pickup, prev, to_status, actor=actor, note=note)

    event_map = {
        PickupRequest.Status.ON_THE_WAY: 'on_the_way',
        PickupRequest.Status.ARRIVED: 'arrived',
        PickupRequest.Status.WEIGHING: 'weighing',
        PickupRequest.Status.COMPLETED: 'completed',
        PickupRequest.Status.CANCELLED: 'cancelled',
    }
    if to_status in event_map:
        _notify(event_map[to_status], pickup)
    return pickup


@transaction.atomic
def collector_advance(*, pickup, collector, to_status=None, note=''):
    if pickup.assigned_collector_id != collector.id:
        raise PermissionDenied('This job is not assigned to you.')

    target = to_status or FORWARD_DEFAULT.get(pickup.status)
    if not target:
        raise ValidationError({'status': 'Cannot advance from this status.'})
    if target == PickupRequest.Status.COMPLETED:
        return complete_pickup(pickup=pickup, actor=collector.user, note=note)
    if target == PickupRequest.Status.CANCELLED:
        return cancel_pickup(pickup=pickup, actor=collector.user, reason=note, as_collector=True)
    return transition(pickup=pickup, to_status=target, actor=collector.user, note=note)


@transaction.atomic
def weigh_items(*, pickup, collector, items):
    if pickup.assigned_collector_id != collector.id:
        raise PermissionDenied('This job is not assigned to you.')
    if pickup.status not in {
        PickupRequest.Status.ARRIVED,
        PickupRequest.Status.WEIGHING,
        PickupRequest.Status.ON_THE_WAY,
    }:
        raise ValidationError({'status': 'Job is not ready to be weighed.'})

    if not items:
        raise ValidationError({'items': 'Provide at least one weighed item.'})

    upsert_items(pickup, items, use_actual=True)
    pickup.refresh_from_db()
    if pickup.status != PickupRequest.Status.WEIGHING:
        transition(pickup=pickup, to_status=PickupRequest.Status.WEIGHING, actor=collector.user, note='Items weighed')
        pickup.refresh_from_db()
    return pickup


@transaction.atomic
def complete_pickup(*, pickup, actor, note=''):
    if pickup.status == PickupRequest.Status.COMPLETED:
        return pickup
    if pickup.status not in {
        PickupRequest.Status.ON_THE_WAY,
        PickupRequest.Status.ARRIVED,
        PickupRequest.Status.WEIGHING,
    }:
        raise ValidationError({'status': f'Cannot complete from {pickup.status}.'})

    recompute_payouts(pickup)
    pickup.refresh_from_db()
    transition(pickup=pickup, to_status=PickupRequest.Status.COMPLETED, actor=actor, note=note or 'Pickup completed')
    pickup.refresh_from_db()
    settle_pickup(pickup)
    return pickup


@transaction.atomic
def cancel_pickup(*, pickup, actor, reason='', as_collector=False):
    if pickup.status == PickupRequest.Status.COMPLETED:
        raise ValidationError({'status': 'Completed pickups cannot be cancelled.'})
    if pickup.status == PickupRequest.Status.CANCELLED:
        return pickup

    allowed = COLLECTOR_CANCELLABLE if as_collector else CUSTOMER_CANCELLABLE
    if pickup.status not in allowed:
        raise ValidationError({'status': f'Cannot cancel a pickup in {pickup.status}.'})

    pickup.cancellation_reason = reason or pickup.cancellation_reason
    pickup.save(update_fields=['cancellation_reason', 'updated_at'])
    return transition(
        pickup=pickup,
        to_status=PickupRequest.Status.CANCELLED,
        actor=actor,
        note=reason or 'Cancelled',
    )


def active_pickups_for_collector(collector):
    return PickupRequest.objects.filter(
        assigned_collector=collector,
        status__in=[
            PickupRequest.Status.ASSIGNED,
            PickupRequest.Status.ON_THE_WAY,
            PickupRequest.Status.ARRIVED,
            PickupRequest.Status.WEIGHING,
        ],
    )
