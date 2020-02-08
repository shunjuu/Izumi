# pylint: disable=import-error
"""
Creates EncoderConfigStore objects to pass down into the system.
"""

from typing import Dict, List

from src.shared.constants.config.encoder_config_store import EncoderConfigStore
from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils
from src.shared.factory.utils.ConfPickleUtils import ConfPickleUtils
from src.shared.factory.utils.PathUtils import PathUtils

class EncoderConf:

    @staticmethod
    def create_encoder_config_store() -> EncoderConfigStore:
        _CONF = ConfLoaderUtils.get_encoder()

        downloading_sources = ConfPickleUtils.clean_downloading_sources(_CONF['downloading']['sources'])
        downloading_rclone_flags = ConfPickleUtils.clean_rclone_flags(_CONF['downloading']['rclone_flags'])
        uploading_destinations = ConfPickleUtils.clean_uploading_destinations(_CONF['uploading']['destinations'])
        uploading_rclone_flags = ConfPickleUtils.clean_rclone_flags(_CONF['uploading']['rclone_flags'])
        endpoints = ConfPickleUtils.clean_endpoints(_CONF['endpoints']['urls'])

        store = EncoderConfigStore(downloading_sources,
                                    downloading_rclone_flags,
                                    uploading_destinations,
                                    uploading_rclone_flags,
                                    endpoints)
        return store