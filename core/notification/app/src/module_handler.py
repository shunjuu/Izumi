import sys
import os

import json

import pprint as pp

# Temp hisha3 for fetching info
from bin import hisha
from bin import hisha2a as hitsu # We need to phase this out in a future module

from src.prints.module_handler_prints import ModuleHandlerPrints

# Individual modules
from src.modules.discord.discord_webhook_module import DiscordWebhookModule

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
        try:
            info.idKitsu = hitsu.hitsu2a(show)['data'][0]['id']
        except:
            pass

        self._logger.info(self._prints.FETCHING_INFO_END)

        return info


    def discord_webhook_notify(self):
        """
        Initiates sending out requests to Discord.
        """

        self._logger.info(self._prints.MODULE_START.format("Discord"))
        dw = DiscordWebhookModule(self._conf, self._reqh, self._printh, self._info)
        fmt = dw.generate_fmt()
        dw.send_notifications(fmt)
        self._logger.info(self._prints.MODULE_END.format("Discord"))


    def notify_all(self):
        """
        Calls all the module notification triggers
        """

        self._logger.warning(self._prints.NOTIFY_ALL_START)
        self.discord_webhook_notify()
        self._logger.warning(self._prints.NOTIFY_ALL_END)
