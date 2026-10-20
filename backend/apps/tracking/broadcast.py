"""Broadcast collector GNSS updates to pickup tracking groups."""
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def broadcast_location(pickup_id, lat, lon, collector_id=None):
    layer = get_channel_layer()
    if layer is None:
        return
    try:
        async_to_sync(layer.group_send)(
            f'tracking_{pickup_id}',
            {
                'type': 'location_update',
                'lat': str(lat),
                'long': str(lon),
                'collector_id': str(collector_id) if collector_id else None,
            },
        )
    except Exception:
        logger.exception('Failed to broadcast location for pickup %s', pickup_id)
