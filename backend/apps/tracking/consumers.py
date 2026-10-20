"""
tracking app – WebSocket consumer for live collector coordinate broadcasting.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer


class CollectorTrackingConsumer(AsyncWebsocketConsumer):
    """
    Customers connect to ws://host/ws/tracking/<pickup_id>/
    Collectors push location via WebSocket or REST; this broadcasts to the group.
    """

    async def connect(self):
        self.pickup_id = self.scope['url_route']['kwargs']['pickup_id']
        self.group_name = f'tracking_{self.pickup_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connected',
            'pickup_id': self.pickup_id,
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Collector pushes: {"lat": 12.34, "long": 56.78}"""
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'error': 'Invalid JSON'}))
            return

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'location_update',
                'lat': data.get('lat'),
                'long': data.get('long'),
                'collector_id': data.get('collector_id'),
            },
        )

    async def location_update(self, event):
        """Broadcast to all group members (customer side)."""
        await self.send(text_data=json.dumps({
            'type': 'location',
            'lat': event.get('lat'),
            'long': event.get('long'),
            'collector_id': event.get('collector_id'),
        }))
