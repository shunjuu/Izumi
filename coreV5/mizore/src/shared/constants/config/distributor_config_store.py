"""
Constant class for storing distributor configurations
"""

from typing import Dict, List

class DistributorConfigStore:

    def __init__(self, ani_t, mal_t, white, s_dl_s, s_dl_f, s_up_d, s_up_f, h_dl_s, h_dl_f, h_up_d, h_up_f, edpts):
        """
        ani_t: str: Anilist tracker filter
        mal_t: str: MyAnimeList tracker filter
        white: List[str]: Whitelisted terms

        s_dl_s: List[str]: List of softsub downloading sources
        s_dl_f: str: Softsub download rclone flags
        s_up_d: List[str]: List of softsub uploading destinations
        s_up_f: str: Softsub upload rclone flags

        h_dl_s: List[str]: List of hardsub downloading sources
        h_dl_f: str: Hardsub download rclone flags
        h_up_d: List[str]: List of hardsub uploading destinations
        h_up_f: str: Hardsub upload rclone flags

        edpts: List[Dict[str, str]]; Endpoints to post
        """

        self._anilist_tracker = ani_t
        self._mal_tracker = mal_t
        self._whitelist = white

        self._softsub_downloading_sources = s_dl_s
        self._softsub_downloading_rclone_flags = s_dl_f
        self._softsub_uploading_destinations = s_up_d
        self._softsub_uploading_rclone_flags = s_up_f

        self._hardsub_downloading_sources = h_dl_s
        self._hardsub_downloading_rclone_flags = h_dl_f
        self._hardsub_uploading_destinations = h_up_d
        self._hardsub_uploading_rclone_flags = h_up_f

        self._endpoints = edpts

    @property
    def anilist_tracker(self) -> str:
        return self._anilist_tracker

    @property
    def mal_tracker(self) -> str:
        return self._mal_tracker

    @property
    def whitelist(self) -> List[str]:
        return self._whitelist

    @property
    def softsub_downloading_sources(self) -> List[str]:
        return self._softsub_downloading_sources

    @property
    def softsub_downloading_rclone_flags(self) -> str:
        return self._softsub_downloading_rclone_flags

    @property
    def softsub_uploading_destinations(self) -> List[str]:
        return self._softsub_uploading_destinations

    @property
    def softsub_uploading_rclone_flags(self) -> str:
        return self._softsub_uploading_rclone_flags

    @property
    def hardsub_downloading_sources(self) -> List[str]:
        return self._hardsub_downloading_sources

    @property
    def hardsub_downloading_rclone_flags(self) -> str:
        return self._hardsub_downloading_rclone_flags

    @property
    def hardsub_uploading_destinations(self) -> List[str]:
        return self._hardsub_uploading_destinations

    @property
    def hardsub_uploading_rclone_flags(self) -> str:
        return self._hardsub_uploading_rclone_flags

    @property
    def endpoints(self) -> List[Dict[str, str]]:
        return self._endpoints