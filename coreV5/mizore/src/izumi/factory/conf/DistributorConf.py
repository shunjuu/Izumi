#pylint: disable=import-error
"""
Creates DistributorConfigStore objects to pass down into the system
"""

from src.shared.constants.config.distributor_config_store import DistributorConfigStore
from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils
from src.shared.factory.utils.ConfPickleUtils import ConfPickleUtils

class DistributorConf:

    @staticmethod
    def create_distributor_config_store() -> DistributorConfigStore:
        _CONF = ConfLoaderUtils.get_distributor()

        anilist_tracker = ConfPickleUtils.format_string(_CONF['trackers']['anilist'])
        mal_tracker = ConfPickleUtils.format_string(_CONF['trackers']['myanimelist'])
        whitelist = ConfPickleUtils.clean_list(_CONF['trackers']['whitelist'])
        endpoints = ConfPickleUtils.clean_endpoints(_CONF['endpoints']['urls'])

        softsub_dl_sources = ConfPickleUtils.clean_downloading_sources(_CONF['softsub']['downloading']['sources'])
        softsub_dl_flags = ConfPickleUtils.clean_rclone_flags(_CONF['softsub']['downloading']['rclone_flags'])
        softsub_up_dests = ConfPickleUtils.clean_uploading_destinations(_CONF['softsub']['uploading']['destinations'])
        softsub_up_flags = ConfPickleUtils.clean_rclone_flags(_CONF['softsub']['uploading']['rclone_flags'])

        hardsub_dl_sources = ConfPickleUtils.clean_downloading_sources(_CONF['hardsub']['downloading']['sources'])
        hardsub_dl_flags = ConfPickleUtils.clean_rclone_flags(_CONF['hardsub']['downloading']['rclone_flags'])
        hardsub_up_dests = ConfPickleUtils.clean_uploading_destinations(_CONF['hardsub']['uploading']['destinations'])
        hardsub_up_flags = ConfPickleUtils.clean_rclone_flags(_CONF['hardsub']['uploading']['rclone_flags'])

        store = DistributorConfigStore(anilist_tracker,
                                        mal_tracker,
                                        whitelist,
                                        softsub_dl_sources,
                                        softsub_dl_flags,
                                        softsub_up_dests,
                                        softsub_up_flags,
                                        hardsub_dl_sources,
                                        hardsub_dl_flags,
                                        hardsub_up_dests,
                                        hardsub_up_flags,
                                        endpoints)
        return store