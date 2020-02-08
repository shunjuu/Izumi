"""
Constant class for storing notifier configurations
"""

from typing import Dict, List

class NotifierConfigStore:

    def __init__(self, ani_t, mal_t, disc_w, edpts, white):
        """
        ani_t: str: Anilist tracker to filter
        mal_t: str: MyAnimeList tracker to filter
        disc_w: List[str]: List of discord webhook urls
        edpts: List[Dict[str, str,]]: Endpoints for POSTing
        white: List[str]: Whitelist terms to auto-pass
        """
        self._anilist_tracker = ani_t
        self._mal_tracker = mal_t
        self._discord_webhooks = disc_w
        self._endpoints = edpts
        self._whitelist = white

    @property
    def anilist_tracker(self) -> str:
        return self._anilist_tracker

    @property
    def mal_tracker(self) -> str:
        return self._mal_tracker

    @property
    def discord_webhooks(self) -> List[str]:
        return self._discord_webhooks

    @property
    def endpoints(self) -> List[Dict[str, str]]:
        return self._endpoints

    @property
    def whitelist(self) -> List[str]:
        return self._whitelist