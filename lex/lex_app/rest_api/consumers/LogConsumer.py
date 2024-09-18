from channels.generic.websocket import AsyncWebsocketConsumer
import json

from lex_app.LexLogger.LexLogger import LexLogger
from lex_app.decorators.LexSingleton import LexSingleton


class LogConsumer(AsyncWebsocketConsumer):
    logger = LexLogger()

    async def connect(self):
        await self.channel_layer.group_add("log_group", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("log_group", self.channel_name)
        await super().disconnect(close_code)


    async def log_message(self, event):
        await self.send(text_data=json.dumps({
            'level': event['level'],
            'message': event['message'],
        }))
    async def receive(self, text_data):
        await self.send(text_data=json.dumps({
            'STATUS': "LexLogger v1.0.0 Created By Hazem Sahbani"
        }))


    # async def log_message(self, event):
    #     await self.send(text_data=json.dumps({
    #         'message': message,
    #     }))
