"""
An "error" class for when user cancels a job with SIGINT, or Docker stop is called.
"""

from inspect import stack, getmodule
from os.path import basename
from typing import Tuple

from src.shared.exceptions.SharedExceptions import SharedException #pylint: disable=import-error

class WorkerCancelledError(SharedException):
    """
    Outside input cancelled job
    Helper indicates whether or not this methdod was called from a helper (to go up by 3 levels instead of 2) 
    """
    def __init__(self, helper: bool = False):
        self.message = "The current job was cancelled externally at {}:{}".format(*WorkerCancelledError._get_calling_details(helper))

    """Get stack trace"""
    @staticmethod
    def _get_calling_details(helper: bool) -> Tuple[str, str]:
        frame = stack()[3] if helper else stack()[2] 
        functionname = str(frame[3]) # The third object in the tuple is the function name
        module = getmodule(frame[0])
        filename = basename(module.__file__)
        return (filename, functionname)