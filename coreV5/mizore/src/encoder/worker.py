"""
This is the central and starting point of the "Encoder" worker
"""


from src.shared.constants.Job import Job #pylint: disable=import-error
from src.shared.exceptions.errors.RcloneError import RcloneError #pylint: disable=import-error
from src.shared.exceptions.errors.WorkerCancelledError import WorkerCancelledError #pylint: disable=import-error
from src.shared.factory.automata.rest.RestSender import RestSender #pylint: disable=import-error
from src.shared.factory.automata.Rclone import Rclone #pylint: disable=import-error
from src.shared.factory.controllers.TempFolderController import TempFolderController #pylint: disable=import-error
from src.shared.factory.utils.JobUtils import JobUtils #pylint: disable=import-error
from src.shared.factory.utils.LoggingUtils import LoggingUtils #pylint: disable=import-error
from src.shared.modules.haikan import Haikan #pylint: disable=import-error

from src.encoder.exceptions.errors.FFmpegError import FFmpegError #pylint: disable=import-error
from src.encoder.factory.automata.FFmpeg import FFmpeg #pylint: disable=import-error
from src.encoder.factory.conf.EncoderConf import EncoderConf #pylint: disable=import-error
from src.encoder.factory.generators.EncodeJobGenerator import EncodeJobGenerator #pylint: disable=import-error


def encode(job: Job) -> None:
    """Job worker"""

    tempfolder = TempFolderController.get_temp_folder()

    try:
        # Step 1: Copy the file from rclone provided source to temp folder
        LoggingUtils.info("[1/7] Starting download of episode file...", color=LoggingUtils.LCYAN)
        src_file = Rclone.download(job, EncoderConf.downloading_sources, tempfolder, EncoderConf.downloading_rclone_flags)

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
        Rclone.upload(hardsub_job, EncoderConf.uploading_destinations, hardsub_file, EncoderConf.uploading_rclone_flags)

        # Step 7: Send POST requests
        LoggingUtils.info("[7/7] Sending POST requests to endpoints...", color=LoggingUtils.LCYAN)
        RestSender.send(JobUtils.to_dict(hardsub_job), EncoderConf.endpoints)

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

    except FFmpegError as fe:

        LoggingUtils.critical(fe.message, color=LoggingUtils.LRED)
        LoggingUtils.critical(fe.output, color=LoggingUtils.RED)
        # In any case, delete the temp folder
        TempFolderController.destroy_temp_folder()

        # Reraise - this will clutter up the logs but make it visible in RQ-dashboard
        raise fe

    except WorkerCancelledError as we:

        LoggingUtils.critical(we.message, color=LoggingUtils.LRED)
        TempFolderController.destroy_temp_folder()

        # Reraise for dashboard
        raise we

    except Exception as e:
        # In the event of an exception, we want to simply log it
        LoggingUtils.critical(e, color=LoggingUtils.LRED)