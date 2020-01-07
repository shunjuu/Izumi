#pylint: disable=import-error

"""
Acts as a routing agent to pass on jobs to the correct methods. 
This seems to be necessary because RQ isn't designed to accomodate 
    different worker methods being pickled (as is a fair assumption in a DS)
"""

# Shared
from src.shared.constants.Job import Job, JobType
from src.shared.factory.utils.LoggingUtils import LoggingUtils

# Workers
from src.encoder import worker as encode_worker
from src.notifier import worker as notify_worker

def route(job: Job) -> None:

    if job.jobtype is JobType.ENCODE:
        LoggingUtils.info("Routing job to Encode", color=LoggingUtils.CYAN)
        encode_worker.encode(job)
    elif job.jobtype is JobType.NOTIFY:
        LoggingUtils.info("Routing job to Notify", color=LoggingUtils.CYAN)
        notify_worker.notify(job)
    else:
        LoggingUtils.critical("Unknown job type, can't route", color=LoggingUtils.LRED)