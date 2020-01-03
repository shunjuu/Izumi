"""
Handles logging control across the entire application
"""

from inspect import stack, getmodule
from os.path import basename
from typing import Tuple

#import inspect
import logging

class LoggingUtils:

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

    logging.basicConfig(format="[%(asctime)s][%(levelname)s]: %(message)s",
                        datefmt="%a|%b%y|%X|%Z")
    logger = logging.getLogger(name="Izumi")
    logger.setLevel(logging.DEBUG)

    LOGGING_STR = "[{}:{}]: {}"

    @classmethod
    def get_logger(cls):
        return cls.logger
    
    @classmethod
    def debug(cls, msg: str, color: str = "") -> None:
        cls.logger.debug("{}{}{}".format(
            color, 
            cls.LOGGING_STR.format(*LoggingUtils.get_calling_details(), msg), 
            cls._ENDC))
    
    @classmethod
    def info(cls, msg: str, color: str = "") -> None:
        cls.logger.info("{}{}{}".format(
            color,
            cls.LOGGING_STR.format(*LoggingUtils.get_calling_details(), msg),
            cls._ENDC))
    
    @classmethod
    def warning(cls, msg: str, color: str = "") -> None:
        cls.logger.warning("{}{}{}".format(
            color,
            cls.LOGGING_STR.format(*LoggingUtils.get_calling_details(), msg),
            cls._ENDC))
    
    @classmethod
    def error(cls, msg: str, color: str = "") -> None:
        cls.logger.error("{}{}{}".format(
            color,
            cls.LOGGING_STR.format(*LoggingUtils.get_calling_details(), msg),
            cls._ENDC))

    @classmethod
    def critical(cls, msg: str, color: str = "") -> None:
        cls.logger.critical("{}{}{}".format(
            color,
            cls.LOGGING_STR.format(*LoggingUtils.get_calling_details(), msg),
            cls._ENDC))
    
    """
    Gets the name of the file that called a logging function for logging output
    """
    @staticmethod
    def get_calling_details() -> Tuple[str, str]:
        frame = stack()[2] # Set to 2, because it's a second level up calling trace
        functionname = str(frame[3]) # The third object in the tuple is the function name
        module = getmodule(frame[0])
        filename = LoggingUtils.get_base_filename(module.__file__)
        return (filename, functionname)

    """
    Gets the basename of the filename, used for logging purposes
    """
    @staticmethod
    def get_base_filename(filename: str) -> str:
        return basename(filename)