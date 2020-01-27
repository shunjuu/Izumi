# pylint: disable=import-error

"""For sending Discord webhook notifications"""

import datetime
import requests
import time

from hurry.filesize import size
from typing import Dict, List

from src.shared.constants.Job import Job
from src.shared.factory.utils.LoggingUtils import LoggingUtils
from src.shared.modules.hisha import HishaInfo

class DiscordWebhook:

    _EMPTY_INFO = "〇〇"

    MAL_ANI_BASE = "https://myanimelist.net/anime/"
    ANI_ANI_BASE = "https://anilist.co/anime/"
    KIT_ANI_BASE = "https://kitsu.io/anime/"
    KIT_DOWN = "https://kitsu.io/"


    @classmethod
    def send(cls, job: Job, hisha: HishaInfo, webhooks: List[str]):

        embed = cls._generate_embed(job, hisha, webhooks)


        LoggingUtils.info("Sending out Discord webhook notifications", color=LoggingUtils.LMAGENTA)
        for webhook in webhooks:
            try:
                requests.post(webhook, json=embed, timeout=5)
            except:
                LoggingUtils.warning("There was an error when sending out a Discord webhook to: {}".format(webhook), color=LoggingUtils.YELLOW)
        LoggingUtils.info("Done sending out webhook notifications", color=LoggingUtils.GREEN)

        return

    @classmethod
    def _generate_embed(cls, job: Job, hisha: HishaInfo, webhooks: List[str]) -> Dict[str, List]:

        webhook = dict()
        webhook['embeds'] = list()

        embed = dict()
        embed['title'] = job.episode

        duration = hisha.duration if hisha.duration != -1 else cls._EMPTY_INFO
        filesize = size(job.filesize) if job.filesize > 0 else cls._EMPTY_INFO
        embed['description'] = "{} mins, {} [{}]".format(duration, filesize, job.sub.capitalize())

        embed['color'] = 65535 if job.sub.lower().startswith('s') else 65280
        embed['timestamp'] = DiscordWebhook._get_timestamp()
        embed['footer'] = {'text': hisha.title_userPreferred}
        embed['thumbnail'] = {'url': hisha.coverImage}
        embed['author'] = {'name': hisha.studio, 'url': hisha.studio_url}

        embed['fields'] = list()

        averageScore = hisha.averageScore if hisha.averageScore != -1 else cls._EMPTY_INFO
        popularity = hisha.popularity if hisha.popularity != -1 else cls._EMPTY_INFO
        episodes = hisha.episodes if hisha.episodes != -1 else cls._EMPTY_INFO
        embed['fields'].append({'name': 'Stats', 'value': 'Score: {}/100, Pop: {}, Total: {} Eps.'.format(averageScore, popularity, episodes)})

        embed['fields'].append({'name': 'Links', 'value': "[MyAnimeList]({}) | [Anilist]({}) | [Kitsu]({})".format(
            str.strip(cls.MAL_ANI_BASE + str(hisha.idMal)),
            str.strip(cls.ANI_ANI_BASE + str(hisha.id)),
            str.strip(cls.KIT_ANI_BASE + str(hisha.idKitsu))
        )})

        webhook['embeds'].append(embed)

        return webhook

    @staticmethod
    def _get_timestamp():
        utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
        utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
        return datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()