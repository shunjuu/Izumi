#pylint: disable=import-error
"""
Util file to help prepare configurations for modules
for pickling.
"""

from typing import Dict, List

from src.shared.factory.utils.PathUtils import PathUtils

class ConfPickleUtils:

    """
    Everything needs to be deep copied out from the TomlDecoder
    """

    @staticmethod
    def clean_downloading_sources(sources: List[str]) -> List[str]:
        sources_copy = list()
        for i in range(len(sources)):
            sources_copy.append(PathUtils.clean_directory_path(sources[i]))
        return sources_copy

    @staticmethod
    def clean_uploading_destinations(dests: List[str]) -> List[str]:
        destinations_copy = list()
        for i in range(len(dests)):
            destinations_copy.append(PathUtils.clean_directory_path(dests[i]))
        return dests

    @staticmethod
    def clean_rclone_flags(flags) -> str:
        return str(flags)

    @staticmethod
    def clean_endpoints(endpoints) -> List[Dict[str, str]]:
        endpoints_copy = list()

        for endpoint in endpoints:
            # Copy each conf
            endpoint_conf = dict()
            endpoint_conf['url'] = endpoint['url']

            # If there's an auth, put it in
            try:
                endpoint_conf['auth'] = endpoint['auth']
            except:
                pass

            endpoints_copy.append(endpoint_conf)

        return endpoints_copy

    @staticmethod
    def clean_list(li) -> List:
        list_copy = list()
        for i in li:
            list_copy.append(i)
        return list_copy

    @staticmethod
    def format_string(st) -> str:
        """Returns the string as it or returns none instead"""
        if st: return st
        return None