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
from src.module_handler import ModuleHandler
from src.print_handler import PrintHandler
from src.prints.notification_prints import NotificationPrints

c = ConfigHandler()
p = PrintHandler(c)
logger = p.get_logger()
np = NotificationPrints(p.Colors())
a = AuthHandler(p)

app = Flask(__name__)

notify_job_queue = Queue()


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
        except:
            pass

        notify_job_queue.task_done()
        logger.warning(np.JOB_COMPLETE)
        print()

@app.route("/notify", methods=['POST'])
def distribute():

    # Headers must be passed in separately, so the request isn't processed
    # before it's confirmed to be authorization.

    print()
    logger.warning(np.NEW_REQUEST)

    a.refresh()
    status = a.authorize(request.headers)

    if not status:
        return "Unauthorized request", 403

    r = RequestHandler(request, p)
    notify_job_queue.put(r)

    return "Request accepted", 200

if __name__ == "__main__":

    logger.warning(np.WORKER_SPAWN.format(c.get_notification_jobs()))

    # Spawn the number of worker threads in the background
    for _ in range(c.get_notification_jobs()):
        encode = Thread(target=encode_worker)
        encode.daemon = True
        encode.start()


    # Start the Flask server
    app.run(host='0.0.0.0', port=c.get_listen_port(), debug=True)

