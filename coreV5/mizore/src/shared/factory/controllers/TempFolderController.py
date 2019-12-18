"""
Handles creating, monitoring, and destroying temporary folders
Because we don't s upport threads, the temp folder is always at:
<project dir path>/.temp/
"""

import shutil
import sys
import tempfile

from src.shared.factory.utils.LoggingUtils import LoggingUtils #pylint: disable=import-error

class TempFolderController:

    TEMP_PATH = str()

    @classmethod
    def get_temp_folder(cls) -> str:
        """
        Returns the path to the temp folder.
        Creates the temp folder if it does not exist.
        """

        if not cls.TEMP_PATH:
            LoggingUtils.debug("No temp folder path detected, creating one.", color=LoggingUtils.YELLOW)
            cls.TEMP_PATH = tempfile.mkdtemp()
            LoggingUtils.debug("Created a temp folder path at {}".format(cls.TEMP_PATH), color=LoggingUtils.GREEN)

        return cls.TEMP_PATH

    @classmethod
    def destroy_temp_folder(cls) -> None:

        if not cls.TEMP_PATH:
            LoggingUtils.debug("No temp folder exists, doing nothing", color=LoggingUtils.GREEN)
            return

        try:
            shutil.rmtree(cls.TEMP_PATH)
            LoggingUtils.debug("Cleared the temp folder path at {}".format(cls.TEMP_PATH), color=LoggingUtils.GREEN)
            cls.TEMP_PATH = str()
        except:
            LoggingUtils.warning("Was unable to clear the temp folder path at {}".format(cls.TEMP_PATH), color=LoggingUtils.RED)