"""
Handles generating Job units from a variety of sources.
We consider this a generator, not a util class - Generators are stored separately.
"""

from src.shared.constants.Job import Job #pylint: disable=import-error

from src.shared.factory.utils.LoggingUtils import LoggingUtils #pylint: disable=import-error

class JobGenerator:

    @staticmethod
    def create_from_json(data: dict) -> Job:
        try:
            LoggingUtils.debug("Creating new Job instance with the following info:", color=LoggingUtils.MAGENTA)
            LoggingUtils.debug("Job.show: {}".format(data['show']), color=LoggingUtils.MAGENTA)
            LoggingUtils.debug("Job.episode: {}".format(data['episode']), color=LoggingUtils.MAGENTA)
            LoggingUtils.debug("Job.filesize: {}".format(data['filesize']), color=LoggingUtils.MAGENTA)
            LoggingUtils.debug("Job.sub: {}".format(data['sub']), color=LoggingUtils.MAGENTA)
            
            return Job(
                data['show'], 
                data['episode'], 
                int(data['filesize']), 
                data['sub'])
        except:
            LoggingUtils.error("Failed to create Job from request - json body is malformed", color=LoggingUtils.RED)
            return None