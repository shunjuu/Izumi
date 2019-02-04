"""
U2 Encoder handles encoding new episodes recently uploaded.
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

# For spawning background threads to encode
from threading import Thread
from queue import Queue

from src.config_handler import ConfigHandler
from src.auth_handler import AuthHandler
from src.request_handler import RequestHandler
from src.os_handler import OSHandler
from src.network_handler import NetworkHandler
from src.print_handler import PrintHandler

# Let flask just use the default name
app = Flask(__name__)

# A queue will act as the source for all encoder threads to pull jobs from
episode_job_queue = Queue() 

c = ConfigHandler()
p = PrintHandler(c)
a = AuthHandler(p)


def encode_worker():
    """
    Represents a single thread that is continuously scanning for a new encode job to do.
    Once it finds one, it takes it and proceses it.
    """
    while True:

        # Fetch the request from the Queue
        new_request = episode_job_queue.get()

        # Process the encoding job here
        """
        o = OSHandler(c, new_request)
        #o._create_temp_dir()
        o.download()
        ofile_size = o.encode()
        sleep(3)
        ofile_name = o.upload()
        sleep(3)
        o.cleanup()

        # Create the NetworkHandler to send out notifications
        n = NetworkHandler(c, new_request, p, ofile_name, ofile_size)
        n.notify_notifiers()
        n.notify_distributors()
        """

        # Mark the job as done
        episode_job_queue.task_done()


@app.route("/encode", methods=['POST'])
def encode():

    # Headers must be passed in separately, so the request isn't processed
    # before it's confirmed to be authorized

    a.refresh() # Refresh in case any auths were made
    status = a.authorize(request.headers)

    if not status:
        return "Unauthorized request", 403

    r = RequestHandler(request, p)
    episode_job_queue.put(r)

    return str(status), 200

if __name__ == "__main__":

    # Spawn the number of worker threads in the background
    for _ in range(c.get_encode_encode_jobs()):
        encode = Thread(target=encode_worker)
        encode.daemon = True
        encode.start()

    # Start the Flask server
    app.run(host='0.0.0.0', port=c.get_listen_port(), debug=True)