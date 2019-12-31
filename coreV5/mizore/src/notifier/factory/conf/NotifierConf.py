# pylint: disable=import-error,no-self-argument

"""
Handles storing configurations for the Notifier.
"""

from typing import Dict, List

from astropy.utils.decorators import classproperty

from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils
from src.shared.factory.utils.PathUtils import PathUtils

class NotifierConf:

    _CONF = ConfLoaderUtils.get_notifier()

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
    def discord_webhooks(cls) -> List[str]:
        """Discord webhook sources"""
        return cls._CONF['modules']['discord-webhook']

    @classproperty
    def endpoints(cls) -> List[Dict[str, str]]:
        """Return a list of dict of endpoints to send post requests"""
        return cls._CONF['endpoints']['urls']

    @classproperty
    def whitelist(cls) -> str:
        """Returns whitelist of terms to check yes"""
        return cls._CONF['trackers']['whitelist']