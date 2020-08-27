# Handles all aspects of logging

import logging

from collections import defaultdict
from dynaconf import settings
from getpass import getuser
from inspect import stack, getmodule, currentframe
from json import dumps
from os.path import basename
from socket import getfqdn
from time import time
from typing import Dict, Tuple

try:
    import pika
    _PIKA_IMPORTED = True
except:
    _PIKA_IMPORTED = False

try:
    import rabbitpy
    _RABBITPY_IMPORTED = True
except:
    _RABBITPY_IMPORTED = False

_AMPQ_EXCHANGE = settings.get("log_exchange", "logs_gateway")
_CONSOLE_FORMAT = settings.get(
    "log_console_format", "[{filename}:{functionname}]: {msg}")
_DATE_FORMAT = settings.get("log_date_format", "%a|%b%y|%X|%Z")
_LOG_FORMAT = settings.get(
    "log_logger_format", "[%(asctime)s][%(levelname)s]: %(message)s")
_LOG_LEVEL = defaultdict(
    lambda: logging.NOTSET,
    {"DEBUG": logging.DEBUG,
     "INFO": logging.INFO,
     "WARNING": logging.WARNING,
     "ERROR": logging.ERROR,
     "CRITICAL": logging.CRITICAL}
)[settings.get("log_level", "INFO").capitalize()]
_LOG_NAME = settings.get("log_name", "izumi")


class AyumiColors:

    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'

    LRED = '\033[91m'
    LGREEN = '\033[92m'
    LYELLOW = '\033[93m'
    LBLUE = '\033[94m'
    LMAGENTA = '\033[95m'
    LCYAN = '\033[96m'

    _ENDC = '\033[0m'


class AyumiHelper(type):

    pika_channel = None
    rabbitpy_channel = None

    logging.basicConfig(format=_LOG_FORMAT, datefmt=_DATE_FORMAT)
    logger = logging.getLogger(name=_LOG_NAME)
    logger.setLevel(_LOG_LEVEL)

    @classmethod
    def get_logger(cls) -> logging.Logger:
        return cls.logger

    @classmethod
    def set_pika_channel(cls, channel) -> None:
        cls.pika_channel = channel

    @classmethod
    def set_rabbitpy_channel(cls, channel) -> None:
        cls.rabbitpy_channel = channel

    @classmethod
    def notset(cls, msg: str, color: str = "") -> None:
        cls._console(msg, color)
        cls._publish(msg, color)

    @classmethod
    def debug(cls, msg: str, color: str = "") -> None:
        cls._console(msg, color)
        cls._publish(msg, color)

    @classmethod
    def info(cls, msg: str, color: str = "") -> None:
        cls._console(msg, color)
        cls._publish(msg, color)

    @classmethod
    def warning(cls, msg: str, color: str = "") -> None:
        cls._console(msg, color)
        cls._publish(msg, color)

    @classmethod
    def critical(cls, msg: str, color: str = "") -> None:
        cls._console(msg, color)
        cls._publish(msg, color)

    @classmethod
    def error(cls, msg: str, color: str = "") -> None:
        cls._console(msg, color)
        cls._publish(msg, color)

    """
    --- ACTUAL FUNCTIONS FOR LOGGING/PUBLISHING/ETC ---
    """

    @classmethod
    def _console(cls, msg: str, color: str) -> None:
        filename, functionname = AyumiHelper.get_calling_details()
        getattr(cls.logger, currentframe().f_back.f_code.co_name)("{}{}{}".format(
            color,
            _CONSOLE_FORMAT.format(
                filename=filename, functionname=functionname, msg=msg
            ),
            AyumiColors._ENDC
        ))

    @classmethod
    def _publish(cls, msg: str, color: str) -> None:

        # Color can be an empty string, so convert that to None for JSON.
        if not color:
            color = None

        # Publish to Pika
        if _PIKA_IMPORTED and cls.pika_channel:
            cls.pika_channel.basic_publish(
                body=dumps({"body": msg, "color": color}),
                exchange=_AMPQ_EXCHANGE,
                routing_key=currentframe().f_back.f_code.co_name.lower(),
                properties=pika.BasicProperties(
                    content_type="application/json",
                    delivery_mode=2,
                    headers=AyumiHelper.get_headers(),
                    timestamp=int(time())
                )
            )

        # Publish to RabbitPy
        if _RABBITPY_IMPORTED and cls.rabbitpy_channel:
            message = rabbitpy.Message(
                cls.rabbitpy_channel,
                dumps({"body": msg, "color": color}),
                properties={
                    "content_type": "application/json",
                    "delivery_mode": 2,
                    "headers": AyumiHelper.get_headers(),
                    "timestamp": int(time())
                })
            message.publish(_AMPQ_EXCHANGE, currentframe().f_back.f_code.co_name.lower())

    @staticmethod
    def get_headers() -> Dict[str, str]:
        return {
            "user": getuser(),
            "host": getfqdn(),
        }

    @staticmethod
    def get_calling_details(level: int = 3) -> Tuple[str, str]:
        """Gets the name of the file that called a logging function for logging output"""
        # Set to 2, because it's a second level up calling trace
        frame = stack()[level]
        # The third object in the tuple is the function name
        functionname = str(frame[3])
        module = getmodule(frame[0])
        filename = AyumiHelper.get_base_filename(module.__file__)
        return (filename, functionname)

    @staticmethod
    def get_base_filename(filename: str) -> str:
        """Gets the basename of the filename, used for logging purposes"""
        return basename(filename)
