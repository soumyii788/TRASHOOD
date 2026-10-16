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
        self.group_name = f"tracking_{self.pickup_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """Collector pushes: {"lat": 12.34, "long": 56.78}"""
        data = json.loads(text_data)
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'location_update',
                'lat': data.get('lat'),
                'long': data.get('long'),
            }
        )

    async def location_update(self, event):
        """Broadcast to all group members (customer side)."""
        await self.send(text_data=json.dumps({
            'lat': event['lat'],
            'long': event['long'],
        }))
