# pylint: disable=import-error
"""
Creates EncoderConf objects to pass down into the system.
"""

from typing import Dict, List

from src.shared.constants.config.encoder_config_store import EncoderConfigStore
from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils
from src.shared.factory.utils.PathUtils import PathUtils

class EncoderConf:

    @staticmethod
    def create_encoder_config_store():
        _CONF = ConfLoaderUtils.get_encoder()

        downloading_sources = EncoderConf._clean_downloading_sources(_CONF['downloading']['sources'])
        downloading_rclone_flags = EncoderConf._clean_rclone_flags(_CONF['downloading']['rclone_flags'])
        uploading_destinations = EncoderConf._clean_uploading_destinations(_CONF['uploading']['destinations'])
        uploading_rclone_flags = EncoderConf._clean_rclone_flags(_CONF['uploading']['rclone_flags'])
        endpoints = _CONF['endpoints']['urls']

        store = EncoderConfigStore(downloading_sources,
                                    downloading_rclone_flags,
                                    uploading_destinations,
                                    uploading_rclone_flags,
                                    endpoints)
        return store

    @staticmethod
    def _clean_downloading_sources(sources: List[str]) -> List[str]:
        for i in range(len(sources)):
            sources[i] = PathUtils.clean_directory_path(sources[i])
        return sources

    @staticmethod
    def _clean_uploading_destinations(dests: List[str]) -> List[str]:
        for i in range(len(dests)):
            dests[i] = PathUtils.clean_directory_path(dests[i])
        return dests

    @staticmethod
    def _clean_rclone_flags(flags) -> str:
        return str(flags)
