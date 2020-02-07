#pylint: disable=import-error
"""
Creates NotifierConf objects to pass down into the system.
"""

from src.shared.constants.config.notifier_config_store import NotifierConfigStore
from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils
from src.shared.factory.utils.ConfPickleUtils import ConfPickleUtils

class NotifierConf:

    @staticmethod
    def create_notifier_config_store() -> NotifierConfigStore:
        _CONF = ConfLoaderUtils.get_notifier()

        anilist_tracker = ConfPickleUtils.format_string(_CONF['trackers']['anilist'])
        mal_tracker = ConfPickleUtils.format_string(_CONF['trackers']['myanimelist'])
        discord_webhooks = ConfPickleUtils.clean_list(_CONF['modules']['discord-webhook'])
        endpoints = ConfPickleUtils.clean_endpoints(_CONF['endpoints']['urls'])
        whitelist = ConfPickleUtils.clean_list(_CONF['trackers']['whitelist'])

        store = NotifierConfigStore(anilist_tracker,
                                    mal_tracker,
                                    discord_webhooks,
                                    endpoints,
                                    whitelist)
        return store