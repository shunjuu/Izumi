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
from src.prints.encode_prints import EncodePrints

# Let flask just use the default name
app = Flask(__name__)

# A queue will act as the source for all encoder threads to pull jobs from
episode_job_queue = Queue() 

c = (ConfigHandler() if 'DOCKER' not in os.environ or not bool(os.environ.get("DOCKER"))
    else ConfigHandler("/src/config.yml")) # Represents ConfigHandler
p = PrintHandler(c) # Represents PrintHandler
logger = p.logger # Represents the logger object
ep = EncodePrints(p.Colors()) # Represents the EncodePrints object
a = (AuthHandler(p) if 'DOCKER' not in os.environ or not bool(os.environ.get("DOCKER"))
    else AuthHandler(p, "/src/auth.yml")) # Represents AuthHandler

def encode_worker():
    """
    Represents a single thread that is continuously scanning for a new encode job to do.
    Once it finds one, it takes it and processes it.
    """
    while True:

        # Fetch the request from the Queue
        new_request = episode_job_queue.get()

        # Process the encoding job here
        try:
            o = OSHandler(c, new_request, p)
            o.download()
            ofile_size = o.encode()
            ofile_name = o.upload()

            # Create the NetworkHandler to send out notifications
            n = NetworkHandler(c, new_request, p, ofile_name, ofile_size)
            n.notify()
            
        except:
            pass

        finally:

            try:
                o.cleanup()
            except:
                pass

        # Mark the job as done
        episode_job_queue.task_done()
        logger.warning(ep.JOB_COMPLETE)


@app.route(c.route, methods=['POST'])
def encode():

    # Headers must be passed in separately, so the request isn't processed
    # before it's confirmed to be authorized

    logger.warning(ep.NEW_REQUEST)

    try:
        a.refresh() # Refresh in case any auths were made
        status = a.authorize(request.headers)

        if not status:
            return "Unauthorized request", 401

        r = RequestHandler(request, p)
        episode_job_queue.put(r)

        return "Request accepted", 200
    except:
        return "Error with request", 400

if __name__ == "__main__":

    logger.warning(ep.WORKER_SPAWN.format(c.encode_encode_jobs))

    # Spawn the number of worker threads in the background
    for _ in range(c.encode_encode_jobs):
        encode = Thread(target=encode_worker)
        encode.daemon = True
        encode.start()

    # Start the Flask server
    app.run(host='0.0.0.0', port=c.listen_port)
