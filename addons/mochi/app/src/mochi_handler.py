import sys
import os

import datetime
import json
import requests
import time

from urllib.parse import quote

from src.prints.mochi_handler_prints import MochiHandlerPrints

TEMPLATE_1 = '''
{{
    "embeds": [
        {{
            "color": {color:d},
            "timestamp": "{timestamp}",
            "footer": {{
                "text": "© Aeri | {show}"  
            }},
            "title": "Mochi Direct URL",
            "description": "{name}: [{episode}]({url})"
        }}
    ]
}}
'''

class MochiHandler:
    """
    Creates that little extra snippet to send for direct links, known as "Mochis"
    """
    def __init__(self, conf, printh):

        self._logger = printh.logger 
        self._prints = MochiHandlerPrints(printh.Colors())
        self._conf = conf
        self._TEMPLATE_1 = TEMPLATE_1

    @staticmethod
    def quote(url):
        """
        Quotes a provided URL to it
        """
        return quote(url, safe=":/")

    def send(self, reqh):
        """
        Sends out the extra snippets to all users
        """

        self._logger.info(self._prints.MOCHI_START)

        discord_webhooks = self._conf.mochi_discord_webhooks

        for hook in discord_webhooks:

            url = hook['base'] + MochiHandler.quote(reqh.show) + "/" + MochiHandler.quote(reqh.episode)

            body = self._TEMPLATE_1.format(
                color = self._load_color(),
                timestamp = self._generate_timestamp(),
                show = reqh.show,
                episode = reqh.episode,
                name = hook['name'],
                url = url)

            try:
                self._logger.info(self._prints.SENDING_REQUEST_START.format(hook['name'], "default"))
                requests.post(hook['url'], json=json.loads(body))
                self._logger.info(self._prints.SENDING_REQUEST_SUCCESS.format(hook['name']))
            except:
                self._logger.warning(self._prints.SENDING_REQUEST_FAIL.format(hook['name']))


    def _generate_timestamp(self):
        """
        Generates the timestamp for the footer
        """
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
        return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

    def _load_color(self):
        """
        Color for the webhook
        """
        return 16711935