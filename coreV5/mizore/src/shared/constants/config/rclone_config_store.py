# pylint: disable=import-error
"""
Stores Rclone config objects to pass as part of jobs.
Passing this enables fully independent works.
"""

import configparser
import os
import tempfile

from src.shared.factory.utils.LoggingUtils import LoggingUtils

class RcloneConfigStore:

        def __init__(self, content: str):
            self._content = content
            self._file = str()

        @property
        def content(self):
            return self._content

        def to_file(self):
            """Writes the config to tempfile. Returns the path to the file"""
            if self._file:
                LoggingUtils.debug("File already exists, returning path at " + self._file)
                return self._file
            else:
                _, self._file = tempfile.mkstemp(suffix=".conf")
                LoggingUtils.debug("Created a new temporary rclone file at " + self._file)
                with open(self._file, 'w') as rconf:
                    rconf.write(self._content)

        def remove_file(self) -> bool:
            """Removes the file. Returns true if succeeded, else false"""
            LoggingUtils.debug("Delecting temp file at: " + self._file)
            if not self._file:
                LoggingUtils.debug("No rclone config file to delete.", color=LoggingUtils.YELLOW)
                return False
            try:
                os.remove(self._file)
                LoggingUtils.debug("Rclone config file successfully deleted.", color=LoggingUtils.GREEN)
                return True
            except:
                LoggingUtils.warning("Rclone config was not able to be deleted - did it exist?", color=LoggingUtils.RED)
                return False
