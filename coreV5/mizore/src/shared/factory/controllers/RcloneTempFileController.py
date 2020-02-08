#pylint:disable=import-error
"""
Handles creating, monitoring, and destroying temporary folders for Rclone.conf.
"""

import os
import sys
import tempfile

from src.shared.constants.config.rclone_config_store import RcloneConfigStore
from src.shared.factory.utils.LoggingUtils import LoggingUtils

class RcloneTempFileController:

    TEMP_PATH = str()

    @classmethod
    def get_temp_file(cls, rcs: RcloneConfigStore) -> str:
        if not cls.TEMP_PATH:
            LoggingUtils.debug("No rclone temp file detected, creating one.", color=LoggingUtils.YELLOW)
            _, cls.TEMP_PATH = tempfile.mkstemp(suffix=".conf")
            with open(cls.TEMP_PATH, 'w') as rconf:
                rconf.write(rcs.content)
            LoggingUtils.debug("Created a temporary file for rclone.conf at " + cls.TEMP_PATH, color=LoggingUtils.GREEN)
        return cls.TEMP_PATH

    @classmethod
    def destroy_temp_file(cls) -> None:

        if not cls.TEMP_PATH:
            LoggingUtils.debug("No rclone tempf ile exists, doing nothing", color=LoggingUtils.GREEN)
            return

        try:
            os.remove(cls.TEMP_PATH)
            LoggingUtils.debug("Cleared the rclone temp file at " + cls.TEMP_PATH, color=LoggingUtils.GREEN)
            cls.TEMP_PATH = str()
        except:
            LoggingUtils.warning("Unable to clear the rclone temp file", color=LoggingUtils.RED)