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

# Don't try any of this here - startup configs should fail immediately
# Initialize in __main__ if
c = None # Represents a ConfigHandler
p = None # Represents PrintHandler
logger = None # Represents the logger object
ep = None # Represents the EncodePrints object
a = None # Represents the authandler object

def _get_config_handler():
    """
    Gets the config path based on if Docker is used or not
    Checks environment for DOCKER='true'
    Returns the appropriate ConfigHandler
    """
    if 'DOCKER' not in os.environ:
        return ConfigHandler()
    else:
        USAGE = bool(os.environ.get("DOCKER"))
        if USAGE:
            return ConfigHandler("/src/config.yml")
        else:
            return ConfigHandler()

def _get_auth_handler(printh):
    """
    Gets the auth path based on if Docker is used or not
    Checks environment for DOCKER='true'
    Returns the appropriate AuthHandler (refresh() not supported)
    Args:
        printh - represents a printh object
    """
    if 'DOCKER' not in os.environ:
        return AuthHandler(printh)
    else:
        USAGE = bool(os.environ.get("DOCKER"))
        if USAGE:
            return AuthHandler(printh, "/src/auth.yml")
        else:
            return AuthHandler(printh)


def distribute_worker():
    """
    Represents a single thread that is continuously scanning for a new distribution job to handle.
    Once it finds one, it takes it and procsses it.
    """

    while True:
        new_request = episode_job_queue.get()

        try:
            o = OSHandler(c, new_request, p)
            o.download()
            o.upload()

            n = NetworkHandler(c, new_request, p)
            n.notify_notifiers()
        except:
            pass
        finally:
            # Always attempt to clean up
            try:
                o.cleanup()
            except:
                pass


        episode_job_queue.task_done()
        logger.warning(dp.JOB_COMPLETE)

@app.route("/distribute", methods=['POST'])
def distribute():

    # Headers must be passed in separately, so the request isn't processeed
    # before it's confirmed to be authorized

    logger.warning(dp.NEW_REQUEST)

    try:
        a.refresh()
        status = a.authorize(request.headers)

        if not status:
            return "Unauthorized request", 401

        r = RequestHandler(request, p)
        episode_job_queue.put(r)
        return "Request accepted", 200
    except:
        return "Error with request", 400

if __name__ == "__main__":

    c = _get_config_handler()
    p = PrintHandler(c)
    logger = p.get_logger()
    ep = EncodePrints(p.Colors())
    a = _get_auth_handler(p)

    logger.warning(dp.WORKER_SPAWN.format(c.get_distributor_jobs()))

    # Spawn the number of worker threads in the background
    for _ in range(c.get_distributor_jobs()):
        distribute = Thread(target=distribute_worker)
        distribute.daemon = True
        distribute.start()

    app.run(host='0.0.0.0', port=c.get_listen_port(), debug=True)
