# pylint: disable=import-error
"""
Handles loading the rclone config into an object we can pass around.
"""

import pprint as pp
import os
import sys

from src.shared.constants.config.rclone_config_store import RcloneConfigStore
from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils
from src.shared.factory.utils.LoggingUtils import LoggingUtils

class RcloneConf:

    _RCI = RcloneConfigStore(ConfLoaderUtils.get_rclone())

    @classmethod
    def get_config(cls) -> RcloneConfigStore:
        return cls._RCI