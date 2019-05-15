import sys
import os

import logging

class PrintHandler():
    """
    Handles shared functions and attributes between all the prints.

    All of the prints are handled through a shared logging class.
    We define Logger.INFO as the "verbose" output, and Logger.WARNING
    and above are always shown.
    """

    class Colors:
        """
        Shell based colors for colored printing!
        Using a class instead of Enum mostly cause Enum is annoying
        """
        HEADER = '\033[95m'
        OKBLUE = '\033[94m'
        OKGREEN = '\033[92m'
        GREEN = '\033[32m'
        BLUE = '\033[01;36m'
        WARNING = '\033[93m'
        LCYAN = '\033[0;96m'
        ORANGE = '\033[0;33m'
        MAGENTA = '\033[35m'
        LMAGENTA = '\033[95m'
        FAIL = '\033[91m'
        ENDC = '\033[0m'
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'


    def __init__(self, conf):
        """
        Args:
            conf - a ConfigHandler that should already be populated.
            Used just to get the verbose settings.
        """

        # Variables
        self._conf = conf
        self._verbose = self._get_verbosity(self._conf)

        self._logger = self._create_logger(self._conf)


    def _get_verbosity(self, conf):
        """
        A method to get whether or not to use verbose prints.
        """
        return conf.get_verbose()

    def _create_logger(self, conf):
        """
        Create the logger and set the levels and output styles.
        """

        # Set the basic config before we create a Logger.
        logging.basicConfig(format=conf.get_logging_logfmt(), 
                            datefmt=conf.get_logging_datefmt())

        # Link it under a name so changes are shared across modules
        logger = logging.getLogger(conf.get_name())

        # Set its level based on verbosity
        # If this is verbose, logger will display Logger.INFO level messages
        # Else, display warning and above
        if conf.get_verbose():
            logger.setLevel(logging.INFO)
        else:
            # For clarity's sake
            logger.setLevel(logging.WARNING)

        return logger

    # Getters

    @property
    def verbose(self):
        """
        Returns whether or not we're worknig verbosely.
        Designed to be called with super().verbose()
        """
        return self._verbose
    
    @property
    def logger(self):
        """
        Gets the logger object that the system will be printing with.
        Alternatively, it should be possible to simply call it with 
        logging.getLogger(conf.get_name())
        """
        return self._logger
    
