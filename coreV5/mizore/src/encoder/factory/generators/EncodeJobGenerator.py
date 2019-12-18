"""
Handles generating Jobs for newly encoded files specifically
"""

from os.path import getsize # use this because Haikan is expensive

from src.shared.constants.Job import Job #pylint: disable=import-error

from src.shared.factory.utils.LoggingUtils import LoggingUtils #pylint: disable=import-error

class EncodeJobGenerator:

    @staticmethod
    def create_job_for_hardsub(src_job: Job, hardsub_file: str) -> Job:

        episode_name = src_job.episode.replace(".mkv", ".mp4")
        episode_filesize = getsize(hardsub_file)
        episode_sub = "hardsub"

        LoggingUtils.debug("Creating new Job instance with the following info:", color=LoggingUtils.MAGENTA)
        LoggingUtils.debug("Job.show: {}".format(src_job.show), color=LoggingUtils.MAGENTA)
        LoggingUtils.debug("Job.episode: {}".format(episode_name), color=LoggingUtils.MAGENTA)
        LoggingUtils.debug("Job.filesize: {}".format(episode_filesize), color=LoggingUtils.MAGENTA)
        LoggingUtils.debug("Job.sub: {}".format(episode_sub), color=LoggingUtils.MAGENTA)
        
        return Job(
            src_job.show,
            src_job.episode.replace(".mkv", ".mp4"),
            getsize(hardsub_file),
            episode_sub)