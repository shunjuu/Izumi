# pylint:disable=import-error
"""
This is the central and starting point of the "Encoder" worker
"""


from src.shared.constants.Job import Job
from src.shared.constants.config.encoder_config_store import EncoderConfigStore
from src.shared.constants.config.rclone_config_store import RcloneConfigStore
from src.shared.exceptions.errors.RcloneError import RcloneError
from src.shared.exceptions.errors.WorkerCancelledError import WorkerCancelledError
from src.shared.factory.automata.rest.RestSender import RestSender
from src.shared.factory.automata.Rclone import Rclone
from src.shared.factory.controllers.RcloneTempFileController import RcloneTempFileController
from src.shared.factory.controllers.TempFolderController import TempFolderController
from src.shared.factory.utils.JobUtils import JobUtils
from src.shared.factory.utils.LoggingUtils import LoggingUtils
from src.shared.modules.haikan import Haikan

from src.encoder.exceptions.errors.FFmpegError import FFmpegError
from src.encoder.factory.automata.FFmpeg import FFmpeg
#from src.encoder.factory.conf.EncoderConf import EncoderConf
from src.encoder.factory.generators.EncodeJobGenerator import EncodeJobGenerator


def encode(job: Job, rconf: RcloneConfigStore, econf: EncoderConfigStore) -> None:
    """Job worker"""

    tempfolder = TempFolderController.get_temp_folder()
    rclone_conf_tempfile = RcloneTempFileController.get_temp_file(rconf)

    try:
        # Step 1: Copy the file from rclone provided source to temp folder
        LoggingUtils.info("[1/7] Starting download of episode file...", color=LoggingUtils.LCYAN)
        src_file = Rclone.download(job, econf.downloading_sources, tempfolder, econf.downloading_rclone_flags)

        # Step 2: Prepare the file (copy over streams, populate metadata, extract subs, etc)
        LoggingUtils.info("[2/7] Preparing episode file for hardsub and extracting subs...", color=LoggingUtils.LCYAN)
        sub1_file, sub2_file = FFmpeg.prepare(job, src_file, tempfolder)

        # Step 3: Add the OpenSans-Semibold.ttf font
        LoggingUtils.info("[3/7] Adding OpenSans-Semibold.ttf font...", color=LoggingUtils.LCYAN)
        FFmpeg.add_font(job, src_file, tempfolder)

        # Step 4: Encode the video using the built in attachments. This also fixes the audio file
        LoggingUtils.info("[4/7] Beginning hardsub encode of episode...", color=LoggingUtils.LCYAN)
        hardsub_file = FFmpeg.hardsub(job, src_file, tempfolder, sub1_file, sub2_file)

        # Step 5: Create a job for our new file
        LoggingUtils.info("[5/7] Creating new Job instance for the hardsubbed file...", color=LoggingUtils.LCYAN)
        hardsub_job = EncodeJobGenerator.create_job_for_hardsub(job, hardsub_file)

        # Step 6: Upload the new file
        LoggingUtils.info("[6/7] Uploading hardsubbed file to destination(s)...", color=LoggingUtils.LCYAN)
        Rclone.upload(hardsub_job, econf.uploading_destinations, hardsub_file, econf.uploading_rclone_flags)

        # Step 7: Send POST requests
        LoggingUtils.info("[7/7] Sending POST requests to endpoints...", color=LoggingUtils.LCYAN)
        RestSender.send(JobUtils.to_dict(hardsub_job), econf.endpoints)

        # Finally, destroy the temp folder and files
        TempFolderController.destroy_temp_folder()
        RcloneTempFileController.destroy_temp_file()

    except RcloneError as re:

        LoggingUtils.critical(re.message, color=LoggingUtils.LRED)
        LoggingUtils.critical("S/D: {} to {}".format(re.source, re.dest), color=LoggingUtils.LRED)
        LoggingUtils.critical(re.output, color=LoggingUtils.RED)
        # In any case, delete the temp folder
        TempFolderController.destroy_temp_folder()
        RcloneTempFileController.destroy_temp_file()

        # Reraise - this will clutter up the logs but make it visible in RQ-dashboard
        raise re

    except FFmpegError as fe:

        LoggingUtils.critical(fe.message, color=LoggingUtils.LRED)
        LoggingUtils.critical(fe.output, color=LoggingUtils.RED)
        # In any case, delete the temp folder
        TempFolderController.destroy_temp_folder()
        RcloneTempFileController.destroy_temp_file()

        # Reraise - this will clutter up the logs but make it visible in RQ-dashboard
        raise fe

    except WorkerCancelledError as we:

        LoggingUtils.critical(we.message, color=LoggingUtils.LRED)
        TempFolderController.destroy_temp_folder()
        RcloneTempFileController.destroy_temp_file()

        # Reraise for dashboard
        raise we

    except Exception as e:
        # In the event of an exception, we want to simply log it
        LoggingUtils.critical(e, color=LoggingUtils.LRED)
        TempFolderController.destroy_temp_folder()
        RcloneTempFileController.destroy_temp_file()

        raise e