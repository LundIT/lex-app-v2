import logging
import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
class WebSocketHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.channel_layer = get_channel_layer()

    def emit(self, record):
        try:
            message = self.format(record)
            async_to_sync(self.channel_layer.group_send)(
                "log_group",
                {
                    "type": "log_message",
                    "message": message,
                    "level": record.levelname,
                }
            )
        except Exception:
            self.handleError(record)
