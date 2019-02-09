import sys
import os

import json

import pprint as pp

# Temp hisha2a for fetching info
from lib import hisha2a

from src.prints.module_handler_prints import ModuleHandlerPrints

# Individual modules
from src.modules.discord.webhook_module import DiscordWebhookModule

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

        # Logging things
        self._logger = printh.get_logger()
        self._prints = ModuleHandlerPrints(printh.Colors())

        self._info = self._get_show_info(self._reqh.get_show())

    def _get_show_info(self, show):
        """ 
        Uses hisha2a to fetch the information 

        Params:
            show - the name of the show in the request
        """

        info = hisha2a.hisha2a(show)
        info['idKitsu'] = hisha2a.hitsu2a(show)['data'][0]['id']
        return info


    def discord_webhook_notify(self):
        """
        Initiates sending out requests to Discord.
        """

        dw = DiscordWebhookModule(self._conf, self._reqh, self._info)
        #pp.pprint(dw._template_1.format(**fmt))


    def notify_all(self):
        """
        Calls all the module notification triggers
        """

        self.discord_webhook_notify()
