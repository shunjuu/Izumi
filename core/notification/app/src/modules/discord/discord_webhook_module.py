import sys
import os

import pprint as pp

import requests
import shutil
import tempfile
import json

import datetime
import time

from hurry.filesize import size
from colorthief import ColorThief

from src.modules.discord.discord_webhook_templates import DiscordWebhookTemplates

from src.prints.modules.discord.discord_webhook_module_prints import DiscordWebhookModulePrints

MAL_ANI_BASE = "https://myanimelist.net/anime/"
ANI_ANI_BASE = "https://anilist.co/anime/"
KIT_ANI_BASE = "https://kitsu.io/anime/"
KIT_DOWN = "https://kitsu.io/"

class DiscordWebhookModule:
    """
    DiscordModule handles sending out webhook notifications
    """

    def __init__(self, conf, reqh, printh, info):

        self._logger = printh.get_logger()
        self._prints = DiscordWebhookModulePrints(printh.Colors())

        self._conf = conf
        self._reqh = reqh
        self._info = info

        # For downloading the cover pic 
        self._temp_dir = None

        # Load the templates
        self._webhook_templates = DiscordWebhookTemplates()
        self._template_1 = self._webhook_templates.get_template_1()

    def generate_fmt(self):
        """
        Generate the dictionary that contains the variable information
        for each request.
        """

        fmt = dict()
        fmt['title'] = self._load_title()
        fmt['mins'] = self._load_duration()
        fmt['size'] = self._load_size()
        fmt['sub_type'] = self._load_sub_type()
        #fmt['color'] = self._generate_colors()
        fmt['color'] = self._pick_colors()
        fmt['timestamp'] = self._generate_timestamp()
        fmt['show_original'] = self._load_original_show()
        fmt['thumbnail_url'] = self._load_thumbnail()
        fmt['score'] = self._load_score()
        fmt['popularity'] = self._load_popularity()
        fmt['eps'] = self._load_eps()
        fmt['mal_url'] = self._load_mal_url()
        fmt['anilist_url'] = self._load_anilist_url()
        fmt['kitsu_url'] = self._load_kitsu_url()

        return fmt

    def send_notifications(self, fmt):
        """
        Sends the notifications to the Discord endpoints
        """

        use_dev = self._conf.get_use_dev()

        if not use_dev:
            # Send notifications out to the configured outpoints

            self._logger.info(self._prints.DEV_DISABLED)

            for hook in self._conf.get_discord_webhook():
                if hook['template'] == 1:
                    body = self._template_1.format(**fmt)
                    try:
                        self._logger.info(self._prints.SENDING_REQUEST_START.format(hook['name'], 1))
                        requests.post(hook['url'], json=json.loads(body))
                        self._logger.info(self._prints.SENDING_REQUEST_SUCCESS.format(hook['name']))
                    except:
                        self._logger.warning(self._prints.SENDING_REQUEST_FAIL.format(hook['name']))

        elif use_dev:
            # Send notifications to the dev hook

            self._logger.info(self._prints.DEV_ENABLED)

            hook = self._conf.get_dev_discord_webhook()
            if hook['template'] == 1:
                body = self._template_1.format(**fmt) 
                try:
                    self._logger.info(self._prints.SENDING_REQUEST_START.format(hook['name'], 1))
                    requests.post(hook['url'], json=json.loads(body))
                    self._logger.info(self._prints.SENDING_REQUEST_SUCCESS.format(hook['name']))
                except:
                    self._logger.warning(self._prints.SENDING_REQUEST_FAIL.format(hook['name']))


    def _load_title(self):
        """
        Gets the title for the dict
        Returns the title as a string
        """

        return self._reqh.episode

    def _load_duration(self):
        """
        Gets the duration of the episode
        Returns it as an integer
        """

        if 'duration' in self._info and self._info['duration']:
            mins = self._info['duration']
        else:
            mins = "〇〇"

        return mins

    def _load_size(self):
        """
        Get the size of the new episode
        Returns the size as a string (using Hurry)
        """

        return size(self._reqh.filesize)

    def _load_sub_type(self):
        """
        Gets the sub type
        Returns it as a string, with the first letter capitalized
        """
        return self._reqh.sub_type.capitalize()

    def _pick_colors(self):
        """
        Returns the predefined decimal colors
        """
        sub_type = self._reqh.sub_type.lower()
        if sub_type == "softsub":
            return 65535
        elif sub_type == "hardsub":
            return 65280

    def _generate_timestamp(self):
        """
        Generates the timestamp for the footer
        """
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
        return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

    def _load_original_show(self):
        """
        Gets the original-language name of the show
        """
        return self._info['title']['native']

    def _load_thumbnail(self):
        """
        Gets the large cover image
        """
        return self._info['coverImage']['large']

    def _load_score(self):
        """
        Returns the score rating of the show, as an integer
        """
        if 'averageScore' in self._info and self._info['averageScore']:
            score = int(self._info['averageScore']) + 10
        else:
            score = "〇〇"

        return score

    def _load_popularity(self):
        """
        Returns the popularity of the show
        """
        if 'popularity' in self._info and self._info['popularity']:
            popularity = self._info['popularity']
        else:
            popularity = "〇〇"

        return popularity

    def _load_eps(self):
        """
        Returns the number of eps in the show
        """
        if 'episodes' in self._info and self._info['episodes']:
            episodes = self._info['duration']
        else:
            episodes = "〇〇"

        return episodes

    def _load_mal_url(self):
        """
        Gets the MAL url and returns it as a string
        """

        return MAL_ANI_BASE + str(self._info['idMal'])
    
    def _load_anilist_url(self):
        """
        Gets the Anilist url and returns it as a string
        """

        return ANI_ANI_BASE + str(self._info['id'])

    def _load_kitsu_url(self):
        """
        Gets the Kitsu url and returns it as a string
        """

        # Kitsu may be down - only return if so
        if self._info['idKitsu']:
            return KIT_ANI_BASE + str(self._info['idKitsu'])

        return KIT_DOWN

# -------------------------------------------------------------------- #

    def _generate_colors(self):
        """
        Generates the decimal colors used for the webhook embeds

        Returns the decimal color value
        """
        # First, download the cover pic into the temp dir
        path = self.__download_thumbnail()
        dom_color = self.__get_dom_color(path)
        hexc = self.__convert_rgb_to_hex(dom_color)
        decc = self.__convert_hex_to_dec(hexc)
        self._cleanup()

        return decc

    # Helper for colors
    def __download_thumbnail(self):
        """
        Downloads the thumbnail into a temp directory
        """

        self.__create_temp_dir() 
        # Get the extension just in case jpg/png
        _, image_ext = os.path.splitext(self._load_thumbnail())
        # Download and save the image
        image_req = requests.get(self._load_thumbnail(), stream=True)

        path = self._temp_dir + "temp" + image_ext
        with open(path, 'wb') as i:
            image_req.raw.decode_content = True
            shutil.copyfileobj(image_req.raw, i)      

        return path

    def __get_dom_color(self, path):
        """
        Use colorthief to get the dominatn color
        Params:
            path - the path to the temporary downloaded thumbnail
        """
        ct = ColorThief(path)
        return ct.get_color(quality=1)

    def __get_palette(self, path):
        """
        Use colorthief to get the two palette colors (as tuples)
        Params:
            path - the path to the temporary downloaded thumbnail
        """
        ct = ColorThief(path)
        return ct.get_palette(color_count=2, quality=1)

    def __convert_rgb_to_hex(self, rgbt):
        """
        Converts the RGB tuple into a hex code
        Params:
            rgbt - RGB tuple
        """
        hexc = '%02x%02x%02x' % rgbt
        return hexc

    def __convert_hex_to_dec(self, hexc):
        """
        Converts the hex value into a decimal value for discord
        Params:
            hexc - a hex string
        """
        dec = int(hexc, 16)
        return dec


    def __create_temp_dir(self):
        """
        Creates a temporary directory and sets the class variable to it.
        """
        try:
            # tempfile.mkdtemp returns the absolute path
            self._temp_dir = tempfile.mkdtemp(dir=sys.path[0])
            # Append a "/" if it's not already there
            if not self._temp_dir.endswith("/"):
                self._temp_dir += "/"

            #self._logger.info(self._prints.TEMP_DIR_CREATE_SUCCESS.format(self._temp_src_dir))

        except Exception as e:
            #self._logger.error(self._prints.TEMP_DIR_CREATE_ERROR)
            os._exit(2)


    def __delete_temp_all(self):
        """
        Deletes the temporary directory and all of its children data.
        In other words, deletes all traces of temp whatsoever.
        """
        #self._logger.warning(self._prints.DELETE_TEMP_FOLDER.format(self._temp_src_dir))
        try:
            shutil.rmtree(self._temp_dir)
            #self._logger.warning(self._prints.DELETE_TEMP_FOLDER_SUCCESS.format(
                #self._temp_src_dir))
        except:
            #self._logger.error(self._prints.DELETE_TEMP_FOLDER_FAIL.format(
                #self._temp_src_dir))
            os._exit(2)


    def _cleanup(self):
        """
        Purge the temporary folder and anything in it
        """

        # Delete the temp folder and everything in it 
        self.__delete_temp_all()