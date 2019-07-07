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

c = (ConfigHandler() if 'DOCKER' not in os.environ or not bool(os.environ.get("DOCKER"))
    else ConfigHandler("/src/config.yml")) # Represents ConfigHandler
p = PrintHandler(c) # Represents PrintHandler
logger = p.logger # Represents the logger object
dp = DistributionPrints(p.Colors()) # Represents the EncodePrints object
a = (AuthHandler(p) if 'DOCKER' not in os.environ or not bool(os.environ.get("DOCKER"))
    else AuthHandler(p, "/src/auth.yml")) # Represents AuthHandler

def distribute_worker():
    """
    Represents a single thread that is continuously scanning for a new distribution job to handle.
    Once it finds one, it takes it and procsses it.
    """

    while True:
        new_request = episode_job_queue.get()

        try:
            o = OSHandler(c, new_request, p)
            if o.check_filters(new_request.show):
                o.distribute()

                n = NetworkHandler(c, new_request, p)
                n.notify()
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

@app.route(c.route, methods=['POST'])
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

    logger.warning(dp.WORKER_SPAWN.format(c.distributor_jobs))

    # Spawn the number of worker threads in the background
    for _ in range(c.distributor_jobs):
        distribute = Thread(target=distribute_worker)
        distribute.daemon = True
        distribute.start()

    app.run(host='0.0.0.0', port=c.listen_port)

