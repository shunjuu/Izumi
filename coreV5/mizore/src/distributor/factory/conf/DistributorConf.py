#pylint: disable=import-error,no-self-argument
"""
Handles storing configurations for the Encoder. These are READONLY properties.
"""

from typing import Dict, List

from astropy.utils.decorators import classproperty

from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils #pylint: disable=import-error
from src.shared.factory.utils.PathUtils import PathUtils #pylint: disable=import-error

class DistributorConf:

    _CONF = ConfLoaderUtils.get_distributor()

    """
    Downloading properties
    """

    @classproperty
    def anilist_tracker(cls) -> str:
        """Returns the anilist tracker account, or None"""
        anilist = cls._CONF['trackers']['anilist']
        if not anilist:
            return None
        return anilist

    @classproperty
    def mal_tracker(cls) -> str:
        """Returns the MAL tracker account, or None"""
        mal = cls._CONF['trackers']['myanimelist']
        if not mal:
            return None
        return mal
        
    @classproperty
    def whitelist(cls) -> str:
        """Returns whitelist of terms to check yes"""
        return cls._CONF['trackers']['whitelist']
    
    # Softsub Rclone

    @classproperty
    def softsub_downloading_sources(cls) -> List[str]:
        """
        Returns a list of downloading sources.
        Each source is guaranteed to end with "/"
        """
        sources = cls._CONF['softsub']['downloading']['sources']
        for i in range(len(sources)):
            sources[i] = PathUtils.clean_directory_path(sources[i])
        return sources
    
    @classproperty
    def softsub_downloading_rclone_flags(cls) -> str:
        """Flags used for rclone when downloading"""
        return str(cls._CONF['softsub']['downloading']['rclone_flags'])
    
    @classproperty
    def softsub_uploading_destinations(cls) -> List[str]:
        """
        Returns the list of destinations to upload to
        Each destination is guaranteed to end with "/"
        """
        dests = cls._CONF['softsub']['uploading']['destinations']
        for i in range(len(dests)):
            dests[i] = PathUtils.clean_directory_path(dests[i])
        return dests

    @classproperty
    def softsub_uploading_rclone_flags(cls) -> str:
        """Flags used for rclone when uploading"""
        return str(cls._CONF['softsub']['uploading']['rclone_flags'])
    
    # Hardsub Rclone

    @classproperty
    def hardsub_downloading_sources(cls) -> List[str]:
        """
        Returns a list of downloading sources.
        Each source is guaranteed to end with "/"
        """
        sources = cls._CONF['hardsub']['downloading']['sources']
        for i in range(len(sources)):
            sources[i] = PathUtils.clean_directory_path(sources[i])
        return sources
    
    @classproperty
    def hardsub_downloading_rclone_flags(cls) -> str:
        """Flags used for rclone when downloading"""
        return str(cls._CONF['hardsub']['downloading']['rclone_flags'])
    
    @classproperty
    def hardsub_uploading_destinations(cls) -> List[str]:
        """
        Returns the list of destinations to upload to
        Each destination is guaranteed to end with "/"
        """
        dests = cls._CONF['hardsub']['uploading']['destinations']
        for i in range(len(dests)):
            dests[i] = PathUtils.clean_directory_path(dests[i])
        return dests

    @classproperty
    def hardsub_uploading_rclone_flags(cls) -> str:
        """Flags used for rclone when uploading"""
        return str(cls._CONF['hardsub']['uploading']['rclone_flags'])
    
    @classproperty
    def endpoints(cls) -> List[Dict[str, str]]:
        """Return a list of dict of endpoints to send post requests"""
        return cls._CONF['endpoints']['urls']
