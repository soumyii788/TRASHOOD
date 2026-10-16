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
        # TODO: Integrate with SMS gateway SDK
        logger.info(f"[SMS] To: {phone_number} | Message: {message}")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task(bind=True, max_retries=3)
def send_push_notification(self, device_token: str, title: str, body: str):
    """
    Send a push notification via FCM / APNs.
    """
    try:
        # TODO: Integrate with Firebase Admin SDK
        logger.info(f"[PUSH] Token: {device_token} | {title}: {body}")
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))


@shared_task
def send_pickup_assigned_notification(pickup_id: str):
    """Notify customer that their pickup has been assigned to a collector."""
    from apps.pickups.models import PickupRequest
    try:
        pickup = PickupRequest.objects.select_related('customer__user').get(pk=pickup_id)
        phone = pickup.customer.user.phone_number
        send_sms_notification.delay(phone, f"Your pickup #{pickup_id[:8]} has been assigned! Track it live.")
    except PickupRequest.DoesNotExist:
        logger.error(f"Pickup {pickup_id} not found for notification.")
