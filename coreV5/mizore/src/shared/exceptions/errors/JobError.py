#pylint: disable=import-error

"""
Errors related to Jobs
"""

from src.shared.constants.Job import Job
from src.shared.factory.utils.JobUtils import JobUtils

from src.shared.exceptions.SharedExceptions import SharedException

class JobError(SharedException):
    """
    Errors that occur related to jobs
    """
    def __init__(self, job: Job, message: str):
        self.message: str = message
        self.job: str = JobUtils.to_jsons(job)

class JobSubTypeError(JobError):
    """When the sub type is not recognized"""
    def __init__(self, job: Job, message: str):
        super().__init__(job, message)