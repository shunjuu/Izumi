"""
U3 Notifications sends user-facing notifications.
"""

# Standard import
import sys
import os 

#Parsing information, if necessary
import json
import yaml

# Web server
from flask import Flask, request
from time import sleep

# For spawning background threads for notificatino
# We do this because sometimes shows can... take more time than we'd like
from threading import Thread 
from queue import Queue

import pprint as pp

# Custom imports
from src.config_handler import ConfigHandler
from src.auth_handler import AuthHandler
from src.request_handler import RequestHandler
from src.network_handler import NetworkHandler
from src.module_handler import ModuleHandler
from src.print_handler import PrintHandler
from src.prints.notification_prints import NotificationPrints

c = None
p = None
logger = None
np = None
a = None

app = Flask(__name__)

notify_job_queue = Queue()

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


def encode_worker():
    """
    Represents a single thread that is continuously scanning for a new distribution job to do.
    Once it finds one, it takes it and processes it.
    """
    while True:
        new_request = notify_job_queue.get()

        try:
            # We need to ignore any errors to keep the queue empty
            m = ModuleHandler(c, new_request, p)
            m.notify_all()

            n = NetworkHandler(c, new_request, p)
            n.notify()
        except Exception as e:
            print(e)
            pass

        notify_job_queue.task_done()
        logger.warning(np.JOB_COMPLETE)
        print()

@app.route("/notify", methods=['POST'])
def distribute():

    # Headers must be passed in separately, so the request isn't processed
    # before it's confirmed to be authorization.

    logger.warning(np.NEW_REQUEST)

    try:
        a.refresh()
        status = a.authorize(request.headers)

        if not status:
            return "Unauthorized request", 401

        r = RequestHandler(request, p)
        notify_job_queue.put(r)

        return "Request accepted", 200
    except:
        return "Error with request", 400

if __name__ == "__main__":

    c = _get_config_handler()
    p = PrintHandler(c)
    logger = p.logger
    np = NotificationPrints(p.Colors())
    a = _get_auth_handler(p)

    logger.warning(np.WORKER_SPAWN.format(c.notification_jobs))

    # Spawn the number of worker threads in the background
    for _ in range(c.notification_jobs):
        encode = Thread(target=encode_worker)
        encode.daemon = True
        encode.start()


    # Start the Flask server
    app.run(host='0.0.0.0', port=c.listen_port)

