"""
Handles sleeping commands needed by the system
"""

from time import sleep

from dep.LoggingUtils import LoggingUtils

class SleepUtils:

    """
    Sleeps for provided seconds with nice output
    """
    @staticmethod
    def sleep(seconds, show_logs = True):
        if show_logs: LoggingUtils.debug("Sleeping {} seconds".format(seconds), color=LoggingUtils.CYAN)
        for i in range(seconds, 0, -1):
            print(str(i) + " ", end="\r")
            sleep(1)
        if show_logs: LoggingUtils.debug("Completed sleeping {} seconds".format(seconds), color=LoggingUtils.CYAN)