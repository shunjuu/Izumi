# pylint: disable=import-error
"""
Handles loading the rclone config into an object we can pass around.
"""

import pprint as pp
import os
import sys

from src.shared.constants.config.rclone_config_store import RcloneConfigStore
from src.shared.factory.utils.LoggingUtils import LoggingUtils

class RcloneConf:

    _RCLONE_PATH = "conf/rclone.conf"
    _rci = None

    try:
        with open(_RCLONE_PATH) as rconf:
            _rci = RcloneConfigStore(rconf.read())
    except:
        # This should run at boot
        LoggingUtils.critical("Error opening your rclone.conf file, is it located at conf/rclone.conf?", color=LoggingUtils.LRED)
        sys.exit()

    @classmethod
    def get_config(cls) -> RcloneConfigStore:
        return cls._rci