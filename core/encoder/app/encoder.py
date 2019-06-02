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


@app.route("/encode", methods=['POST'])
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

    # Set the variables
    c = _get_config_handler()
    p = PrintHandler(c)
    logger = p.logger
    ep = EncodePrints(p.Colors())
    a = _get_auth_handler(p)

    logger.warning(ep.WORKER_SPAWN.format(c.encode_encode_jobs))

    # Spawn the number of worker threads in the background
    for _ in range(c.encode_encode_jobs):
        encode = Thread(target=encode_worker)
        encode.daemon = True
        encode.start()

    # Start the Flask server
    app.run(host='0.0.0.0', port=c.listen_port)
