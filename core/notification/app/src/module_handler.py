import sys
import os

import json

import pprint as pp

# Temp hisha3 for fetching info
from bin import hisha # for information fetching
from bin import akari # for MAL filtering
from bin import kishi # for Anilist filtering

from src.prints.module_handler_prints import ModuleHandlerPrints

# Individual modules
from src.modules.discord.discord_webhook_module import DiscordWebhookModule
from src.modules.fbchat.fbchat_module import FBChatModule

class ModuleHandler:
    """
    Takes an incoming requests, grabs information from anilist, and
    passes it to all the modules. 
    """

    def __init__(self, conf, reqh, printh):
        """
        Args:
            conf - A ConfigHandler object
            reqh - A RequestHandler object
            printh - A PrintHandler object
        """

        self._conf = conf
        self._reqh = reqh
        self._printh = printh

        self._hisha = hisha.Hisha()
        self._akari = akari.Akari()
        self._kishi = kishi.Kishi()

        # Logging things
        self._logger = printh.logger
        self._prints = ModuleHandlerPrints(printh.Colors())

        self._info = self._get_show_info(self._reqh.show)

    def _get_show_info(self, show):
        """ 
        Uses hisha and hitsu to fetch the information 

        Params:
            show - the name of the show in the request
        """

        self._logger.info(self._prints.FETCHING_INFO_START)
        info = self._hisha.search(show)
        self._logger.info(self._prints.FETCHING_INFO_END)

        return info

    def _check_filters(self, show):
        """
        Use Akari and Kishi to check if a given user's profile is watching this show.
        Used to filter whether or not notifications should be sent.

        If either profile returns True, return True

        Params:
            show - the name of the show in the request

        Returns: a boolean indicating whether or not the show is being watched
        """

        ani_user = self._conf.notification_filter_anilist
        mal_user = self._conf.notification_filter_mal

        # If neither are being used, then return true by default
        if not ani_user and not mal_user:
            self._logger.info(self._prints.FILTER_NOT_USED)
            return True

        # Check both by ID and Names
        if ani_user:
            if self._kishi.is_user_watching_id(ani_user, self._info.id): 
                self._logger.info(self._prints.FILTER_FOUND.format(show, "Anilist", ani_user, "id"))
                return True
            if self._kishi.is_user_watching_names(ani_user, show): 
                self._logger.info(self._prints.FILTER_FOUND.format(show, "Anilist", ani_user, "name"))
                return True

        if mal_user:
            if self._akari.is_user_watching_id(mal_user, self._info.idMal): 
                self._logger.info(self._prints.FILTER_FOUND.format(show, "MyAnimeList", mal_user, "id"))
                return True
            if self._akari.is_user_watching_names(mal_user, show): 
                self._logger.info(self._prints.FILTER_FOUND.format(show, "MyAnimeList", mal_user, "name"))
                return True

        # All checks failed, so return False
        self._logger.info(self._prints.FILTER_SHOW_NOT_FOUND.format(show))
        return False

    def discord_webhook_notify(self):
        """
        Initiates sending out requests to Discord.
        """

        self._logger.info(self._prints.MODULE_START.format("Discord"))
        dw = DiscordWebhookModule(self._conf, self._reqh, self._printh, self._info)
        fmt = dw.generate_fmt()
        dw.send_notifications(fmt)
        self._logger.info(self._prints.MODULE_END.format("Discord"))

    def fbchat_notify(self):
        """
        Initiates sending out notifs to FBChat
        """
        self._logger.info(self._prints.MODULE_START.format("FBChat"))
        fbcm = FBChatModule(self._conf, self._reqh, self._printh, self._info)
        fbcm.send_notifications()
        self._logger.info(self._prints.MODULE_END.format("FBChat"))


    def notify_all(self):
        """
        Calls all the module notification triggers
        """
        # Only run it if filters are green
        if self._check_filters(self._reqh.show):

            self._logger.warning(self._prints.NOTIFY_ALL_START)
            self.discord_webhook_notify()
            self.fbchat_notify()
            self._logger.warning(self._prints.NOTIFY_ALL_END)
