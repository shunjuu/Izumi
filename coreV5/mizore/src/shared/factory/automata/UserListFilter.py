# pylint: disable=import-error,no-self-argument

"""Handles checking if user is watching a given show or not"""

from typing import List

from src.shared.constants.Job import Job
from src.shared.factory.utils.LoggingUtils import LoggingUtils
from src.shared.modules.akari import Akari
from src.shared.modules.hisha import HishaInfo
from src.shared.modules.kishi import Kishi

class UserListFilter:

    _AKARI = Akari()
    _KISHI = Kishi()

    @classmethod
    def check(cls, job: Job, info: HishaInfo, anilist: str, mal: str, whitelist: List[str]) -> bool:
        """
        Checks whether or not user is watching show.
        If anilist and mal both aren't active, returns True
        If either are active, it will check either (or both). If is watching on either, return true
        If show name has whitelisted term in it, return true
        Otherwise, returns false
        """

        # If neither are being used, it's true by default
        if not anilist and not mal:
            LoggingUtils.info("No filters are being used, checks passed", color=LoggingUtils.GREEN)
            return True

        # Check our whitelist
        for term in whitelist:
            if term in job.show.lower() or term in info.title_english.lower():
                LoggingUtils.info("Term {} is whitelisted and in show name, returning True".format(term), color=LoggingUtils.GREEN)
                return True

        # If anilist is provided, check it
        if anilist:
            if cls._KISHI.is_user_watching_id(anilist, info.id):
                LoggingUtils.debug("Check passed for Anilist via ID")
                LoggingUtils.info("User is watching show on Anilist, returning True", color=LoggingUtils.GREEN)
                return True
            if cls._KISHI.is_user_watching_names(anilist, info.title_english):
                LoggingUtils.debug("Check passed for Anilist via Hisha show name")
                LoggingUtils.info("User is watching show on Anilist, returning True", color=LoggingUtils.GREEN)
                return True
            if cls._KISHI.is_user_watching_names(anilist, job.show):
                LoggingUtils.debug("Check passed for Anilist via origin show name")
                LoggingUtils.info("User is watching show on Anilist, returning True", color=LoggingUtils.GREEN)
                return True

        if mal:
            if cls._AKARI.is_user_watching_id(mal, info.idMal):
                LoggingUtils.debug("Check passed for MyAnimeList via ID")
                LoggingUtils.info("User is watching show on MyAnimeList, returning True", color=LoggingUtils.GREEN)
                return True
            if cls._AKARI.is_user_watching_names(mal, info.title_english):
                LoggingUtils.debug("Check passed for MyAnimeList via Hisha show name")
                LoggingUtils.info("User is watching show on MyAnimeList, returning True", color=LoggingUtils.GREEN)
                return True
            if cls._AKARI.is_user_watching_names(mal, job.show):
                LoggingUtils.debug("Check passed for MyAnimeList via origin show name")
                LoggingUtils.info("User is watching show on MyAnimeList, returning True", color=LoggingUtils.GREEN)
                return True

        LoggingUtils.info("Didn't find the show in any given filter, returning False", color=LoggingUtils.YELLOW)
        return False