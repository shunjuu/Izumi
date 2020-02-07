#pylint: disable=import-error

"""
This is the central and starting point of the "Notify" worker
"""
import pprint

from src.notifier.factory.automata.discord.webhook import DiscordWebhook

from src.shared.constants.Job import Job
from src.shared.factory.automata.UserListFilter import UserListFilter
from src.shared.factory.automata.rest.RestSender import RestSender
from src.shared.factory.utils.JobUtils import JobUtils
from src.shared.factory.utils.LoggingUtils import LoggingUtils
from src.shared.modules.hisha import Hisha

from src.shared.constants.config.notifier_config_store import NotifierConfigStore

hisha = Hisha()

def notify(job: Job, nconf: NotifierConfigStore) -> None:
    """Notify worker"""

    try:
        # 1. Get the info of the show
        LoggingUtils.info("[1/X] Fetching show information via Hisha...", color=LoggingUtils.CYAN)
        info = hisha.search(job.show)

        # 2. Check filters
        LoggingUtils.info("[2/X] Checking user list filters...", color=LoggingUtils.CYAN)
        filters = UserListFilter.check(job, info, nconf.anilist_tracker, nconf.mal_tracker, nconf.whitelist)
        if not filters:
            LoggingUtils.info("User isn't watching this show, concluding job immediately.", color=LoggingUtils.LYELLOW)
            return False

        # 3. First automata: Start sending Discord webhooks
        LoggingUtils.info("[3/X] Sending Discord Webhook Notifications...", color=LoggingUtils.CYAN)
        DiscordWebhook.send(job, info, nconf.discord_webhooks)

        # 4. Send POST requests
        LoggingUtils.info("[4/X] Sending POST requests to endpoints...", color=LoggingUtils.CYAN)
        RestSender.send(JobUtils.to_dict(job), nconf.endpoints)

    except Exception as e:
        # In the event of an exception, we want to simply log it
        LoggingUtils.critical(e, color=LoggingUtils.LRED)
        raise e
