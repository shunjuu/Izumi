"""
U4 Distribution handles distributing new episodes recently uploaded.
"""

# Standard import
import sys
import os

# Parsing information
import json
import yaml

# Web server
from flask import Flask, request
from time import sleep

# For spawning background threads to distribute
from threading import Thread
from queue import Queue

from src.config_handler import ConfigHandler
from src.auth_handler import AuthHandler
from src.request_handler import RequestHandler
from src.os_handler import OSHandler
from src.network_handler import NetworkHandler
from src.print_handler import PrintHandler
from src.prints.distribution_prints import DistributionPrints

app = Flask(__name__)

episode_job_queue = Queue()

c = ConfigHandler(cpath="/conf/config.yml")
p = PrintHandler(c)
logger = p.get_logger()
dp = DistributionPrints(p.Colors())
a = AuthHandler(p, apath="/conf/auth.yml")

def distribute_worker():
    """
    Represents a single thread that is continuously scanning for a new distribution job to handle.
    Once it finds one, it takes it and procsses it.
    """

    while True:
        new_request = episode_job_queue.get()

        o = OSHandler(c, new_request, p)
        o.download()
        o.upload()
        o.cleanup()

        n = NetworkHandler(c, new_request, p)
        n.notify_notifiers()

        episode_job_queue.task_done()
        logger.warning(dp.JOB_COMPLETE)
        print()

@app.route("/distribute", methods=['POST'])
def distribute():

    # Headers must be passed in separately, so the request isn't processeed
    # before it's confirmed to be authorized

    print()
    logger.warning(dp.NEW_REQUEST)

    a.refresh()
    status = a.authorize(request.headers)

    if not status:
        return "Unauthorized request", 403

    r = RequestHandler(request, p)
    episode_job_queue.put(r)

    return "Request accepted", 200

if __name__ == "__main__":

    logger.warning(dp.WORKER_SPAWN.format(c.get_distributor_jobs()))

    # Spawn the number of worker threads in the background
    for _ in range(c.get_distributor_jobs()):
        distribute = Thread(target=distribute_worker)
        distribute.daemon = True
        distribute.start()

    app.run(host='0.0.0.0', port=c.get_listen_port(), debug=True)
