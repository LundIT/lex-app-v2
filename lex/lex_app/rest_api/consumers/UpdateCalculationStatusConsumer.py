import json

from channels.generic.websocket import AsyncWebsocketConsumer


class UpdateCalculationStatusConsumer(AsyncWebsocketConsumer):
    active_consumers = set()
    async def connect(self):
        await self.channel_layer.group_add(f'update_calculation_status', self.channel_name)
        await self.accept()
        self.active_consumers.add(self)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(f'update_calculation_status', self.channel_name)
        await super().disconnect(close_code)

    async def calculation_is_completed(self, event):
        payload = event['payload']
        await self.send(text_data=json.dumps({
            'type': 'calculation_is_completed',
            'payload': payload
        }))
    @classmethod
    async def disconnect_all(cls):
        for consumer in cls.active_consumers.copy():
            await consumer.disconnect(None)
