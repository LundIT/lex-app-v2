# custom_logger.py

import logging
import json
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from lex_app.LexLogger.WebSockerHandler import WebSocketHandler
from lex_app.decorators.LexSingleton import LexSingleton


class LexLogLevel:
    VERBOSE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

@LexSingleton
class LexLogger:
    def __init__(self):
        self.logger = None
        self._initialize_logger()

    def _initialize_logger(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LexLogLevel.VERBOSE)

        # Add custom log level
        logging.addLevelName(LexLogLevel.VERBOSE, "VERBOSE")

        # Create handlers
        console_handler = logging.StreamHandler()
        file_handler = logging.FileHandler(settings.LOG_FILE_PATH)
        websocket_handler = WebSocketHandler()

        # Set levels for handlers
        console_handler.setLevel(LexLogLevel.WARNING)
        file_handler.setLevel(LexLogLevel.VERBOSE)
        websocket_handler.setLevel(LexLogLevel.VERBOSE)

        # Create formatters and add them to handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        websocket_handler.setFormatter(formatter)

        # Add handlers to the logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(websocket_handler)

    def verbose(self, message):
        self.logger.log(LexLogLevel.VERBOSE, message)

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)
