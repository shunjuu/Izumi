"""
Handles storing configurations for the Encoder. These are READONLY properties.
"""

from typing import Dict, List

from astropy.utils.decorators import classproperty

from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils #pylint: disable=import-error
from src.shared.factory.utils.PathUtils import PathUtils #pylint: disable=import-error

class EncoderConf:

    _CONF = ConfLoaderUtils.get_encoder()

    """
    Downloading properties
    """

    #pylint: disable=no-self-argument
    @classproperty
    def downloading_sources(cls) -> List[str]:
        """
        Returns a list of downloading sources.
        Each source is guaranteed to end with "/"
        """
        sources = cls._CONF['downloading']['sources']
        for i in range(len(sources)):
            sources[i] = PathUtils.clean_directory_path(sources[i])
        return sources

    #pylint: disable=no-self-argument
    @classproperty
    def downloading_rclone_flags(cls) -> str:
        """Flags used for rclone when downloading"""
        return str(cls._CONF['downloading']['rclone_flags'])

    #pylint: disable=no-self-argument
    @classproperty
    def uploading_destinations(cls) -> List[str]:
        """
        Returns the list of destinations to upload to
        Each destination is guaranteed to end with "/"
        """
        dests = cls._CONF['uploading']['destinations']
        for i in range(len(dests)):
            dests[i] = PathUtils.clean_directory_path(dests[i])
        return dests

    #pylint: disable=no-self-argument
    @classproperty
    def uploading_rclone_flags(cls) -> str:
        """Flags used for rclone when uploading"""
        return str(cls._CONF['uploading']['rclone_flags'])

    #pylint: disable=no-self-argument
    @classproperty
    def endpoints(cls) -> List[Dict[str, str]]:
        """Return a list of dict of endpoints to send post requests"""
        return cls._CONF['endpoints']['urls']
