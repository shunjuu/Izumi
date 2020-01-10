#pylint:disable=import-error

"""
This is the central and starting point of the "Distributor" worker
"""

from src.distributor.factory.conf.DistributorConf import DistributorConf

from src.shared.constants.Job import Job
from src.shared.factory.automata.UserListFilter import UserListFilter
from src.shared.factory.automata.Rclone import Rclone
from src.shared.factory.automata.rest.RestSender import RestSender
from src.shared.factory.controllers.TempFolderController import TempFolderController
from src.shared.factory.utils.JobUtils import JobUtils
from src.shared.factory.utils.LoggingUtils import LoggingUtils
from src.shared.modules.hisha import Hisha

from src.shared.exceptions.errors.RcloneError import RcloneError
from src.shared.exceptions.errors.JobError import JobSubTypeError

hisha = Hisha()

def distribute(job: Job) -> None:
    """Job worker"""

    tempfolder = TempFolderController.get_temp_folder()

    try:
        # Step 1: Check if we should even download the show
        LoggingUtils.info("[1/X] Fetching show information via Hisha...", color=LoggingUtils.CYAN)
        info = hisha.search(job.show)

        # Step 2: Check filter
        LoggingUtils.info("[2/X] Checking user list filters...", color=LoggingUtils.CYAN)
        filters = UserListFilter.check(job, info, DistributorConf.anilist_tracker, DistributorConf.mal_tracker, DistributorConf.whitelist)
        if not filters:
            LoggingUtils.info("User isn't watching this show, concluding job immediately.", color=LoggingUtils.LYELLOW)
            return False
        
        # Step 3: Download the file
        LoggingUtils.info("[3/5] Starting download of episode file...", color=LoggingUtils.LCYAN)

        sources = None
        flags = None

        if job.sub.lower() == "softsub":
            LoggingUtils.info("Softsub mode detected, loading softsub download configs", color=LoggingUtils.CYAN)
            sources = DistributorConf.softsub_downloading_sources
            flags = DistributorConf.softsub_downloading_rclone_flags
        elif job.sub.lower() == "hardsub":
            LoggingUtils.info("Hardsub mode detected, loading hardsub download configs", color=LoggingUtils.CYAN)
            sources = DistributorConf.hardsub_downloading_sources
            flags = DistributorConf.hardsub_downloading_rclone_flags
        else:
            raise JobSubTypeError(job, "Unknown sub type {}".format(job.sub))
        
        src_file = Rclone.download(job, sources, tempfolder, flags)

        # Step 4: Upload it elsewhere
        LoggingUtils.info("[4/5] Uploading hardsubbed file to destination(s)...", color=LoggingUtils.LCYAN)
        
        destinations = None
        flags = None

        if job.sub.lower() == "softsub":
            LoggingUtils.info("Softsub mode detected, loading softsub upload configs", color=LoggingUtils.CYAN)
            destinations = DistributorConf.softsub_uploading_destinations
            flags = DistributorConf.softsub_uploading_rclone_flags
        elif job.sub.lower() == "hardsub":
            LoggingUtils.info("Hardsub mode detected, loading hardsub upload configs", color=LoggingUtils.CYAN)
            destinations = DistributorConf.hardsub_uploading_destinations
            flags = DistributorConf.hardsub_uploading_rclone_flags
        else:
            raise JobSubTypeError(job, "Unknown sub type {}".format(job.sub))

        Rclone.upload(job, destinations, src_file, flags)

        # Step 5: Send POST requests
        LoggingUtils.info("[5/5] Sending POST requests to endpoints...", color=LoggingUtils.LCYAN)
        RestSender.send(JobUtils.to_dict(job), DistributorConf.endpoints)

        # Finally, destroy the temp folder
        TempFolderController.destroy_temp_folder()
    
    except RcloneError as re:

        LoggingUtils.critical(re.message, color=LoggingUtils.LRED)
        LoggingUtils.critical("S/D: {} to {}".format(re.source, re.dest), color=LoggingUtils.LRED)
        LoggingUtils.critical(re.output, color=LoggingUtils.RED)
        # In any case, delete the temp folder
        TempFolderController.destroy_temp_folder()

        # Reraise - this will clutter up the logs but make it visible in RQ-dashboard
        raise re

    except JobSubTypeError as jste:

        LoggingUtils.critical(jste.message, color=LoggingUtils.LRED)
        LoggingUtils.critical("Job: {}".format(jste.job), color=LoggingUtils.LRED)
        TempFolderController.destroy_temp_folder()

        raise jste

    except Exception as e:
        # In the event of an exception, we want to simply log it
        LoggingUtils.critical(e, color=LoggingUtils.LRED)
        raise e