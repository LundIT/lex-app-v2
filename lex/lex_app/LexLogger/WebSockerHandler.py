import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class WebSocketHandler(logging.Handler):
    DJANGO_TO_REACT_MAPPER = {
        'calculation_id': 'id',
        'log_id': 'logId',
        'class_name': 'logName',
        'details': 'logDetails',
        'trigger_name': 'triggerName',
        'message': 'message',
        'level': 'level',
        'log_message': 'type',
        'timestamp': 'timestamp',
        'method': 'method',
    }

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
                    "logName": getattr(record, 'class_name', 'N/A'),
                    "triggerName": getattr(record, 'trigger_name', 'N/A'),
                    "logDetails": getattr(record, 'details', 'N/A'),
                    "id": getattr(record, 'calculation_id', 'N/A'),
                    "logId": getattr(record, 'log_id', 'N/A'),
                    "timestamp": str(record.created),
                    "method": record.funcName,
                }
            )
        except Exception:
            self.handleError(record)
