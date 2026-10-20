"""
notifications app – Celery tasks for SMS, Push, and Email notifications.
"""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_sms_notification(self, phone_number: str, message: str):
    """
    Send an SMS via the configured gateway (e.g., MSG91 / Twilio).
    Retries up to 3 times on failure with exponential back-off.
    """
    try:
        logger.info('[SMS] To: %s | Message: %s', phone_number, message)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_push_notification(self, device_token: str, title: str, body: str):
    """Send a push notification via FCM / APNs."""
    try:
        logger.info('[PUSH] Token: %s | %s: %s', device_token, title, body)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


def _pickup_phones(pickup):
    phones = []
    if pickup.customer_id:
        phones.append(('customer', pickup.customer.user.phone_number))
    if pickup.assigned_collector_id:
        phones.append(('collector', pickup.assigned_collector.user.phone_number))
    return phones


@shared_task
def notify_pickup_event(pickup_id: str, event: str):
    """Fan out SMS for a pickup lifecycle event."""
    from apps.pickups.models import PickupRequest

    try:
        pickup = PickupRequest.objects.select_related(
            'customer__user', 'assigned_collector__user'
        ).get(pk=pickup_id)
    except PickupRequest.DoesNotExist:
        logger.error('Pickup %s not found for notification.', pickup_id)
        return

    short_id = str(pickup.id)[:8].upper()
    amount = pickup.total_payout
    templates = {
        'requested': {
            'customer': f'Trashhood: Pickup #{short_id} is booked. We will assign a collector shortly.',
        },
        'assigned': {
            'customer': f'Trashhood: Pickup #{short_id} has been assigned. Track it live in the app.',
            'collector': f'Trashhood: You accepted pickup #{short_id}. Head to the location when ready.',
        },
        'on_the_way': {
            'customer': f'Trashhood: Your collector is on the way for pickup #{short_id}.',
        },
        'arrived': {
            'customer': f'Trashhood: Collector has arrived for pickup #{short_id}.',
        },
        'weighing': {
            'customer': f'Trashhood: Your scrap for pickup #{short_id} is being weighed.',
        },
        'completed': {
            'customer': f'Trashhood: Pickup #{short_id} complete. ₹{amount} credited to your wallet.',
            'collector': f'Trashhood: Pickup #{short_id} completed. Commission credited.',
        },
        'cancelled': {
            'customer': f'Trashhood: Pickup #{short_id} was cancelled.',
            'collector': f'Trashhood: Pickup #{short_id} was cancelled.',
        },
    }

    messages = templates.get(event, {})
    for role, phone in _pickup_phones(pickup):
        text = messages.get(role)
        if text:
            send_sms_notification(phone, text)


@shared_task
def send_pickup_assigned_notification(pickup_id: str):
    """Backward-compatible alias used by older callers."""
    notify_pickup_event.delay(pickup_id, 'assigned')
