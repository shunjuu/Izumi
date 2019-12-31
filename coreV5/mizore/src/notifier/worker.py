#pylint: disable=import-error

"""
This is the central and starting point of the "Notify" worker
"""
import pprint

from src.notifier.factory.conf.NotifierConf import NotifierConf

from src.shared.constants.Job import Job
from src.shared.factory.automata.UserListFilter import UserListFilter
from src.shared.factory.utils.LoggingUtils import LoggingUtils
from src.shared.modules.hisha import Hisha

hisha = Hisha()

def notify(job: Job) -> None:
    """Notify worker"""

    print("Got the job!")

    try:
        # 1. Get the info of the show
        LoggingUtils.info("[1/X] Fetching show information via Hisha...", color=LoggingUtils.CYAN)
        info = hisha.search(job.show)

        # 2. Check filters
        LoggingUtils.info("[2/X] Checking user list filters...", color=LoggingUtils.CYAN)
        filters = UserListFilter.check(job, info, NotifierConf.anilist_tracker, NotifierConf.mal_tracker, NotifierConf.whitelist)
        if not filters:
            LoggingUtils.info("User isn't watching this show, concluding job immediately.", color=LoggingUtils.LYELLOW)
            return False

    except Exception as e:
        print(e)
    