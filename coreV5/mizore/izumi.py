"""
This is the application-level FLask server that handles all incoming requests.
"""

# Basic imports
import logging
import json
import pickle
import os
import signal
import sys
import yaml

from time import sleep

# Custom imports
from src.shared.factory.automata.auth.RequestAuthorizer import RequestAuthorizer
from src.shared.factory.generators.JobGenerator import JobGenerator
from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils
from src.shared.factory.utils.LoggingUtils import LoggingUtils

from src.izumi.factory.conf.IzumiConf import IzumiConf

# Workers
from src.encoder.worker import encode as encode_worker
from src.notifier.worker import notify as notify_worker

# Flask imports
from flask import Flask, jsonify, request

# Distributed System imports
pickle.HIGHEST_PROTOCOL = 4 # Force to use Protocol 4 to support modern Python systems
import rq_dashboard
from redis import Redis
#from rq import Queue
from src.rq.rq import Queue

from redis.exceptions import ConnectionError as RedisConnectionError

# Signal handler
def sig_handler(sig, frame):
    LoggingUtils.critical("SIG command {} detected, exiting...".format(sig), color=LoggingUtils.LRED)
    sys.exit()
# Add in SIGKILL handler
signal.signal(signal.SIGINT, sig_handler)
signal.signal(signal.SIGTERM, sig_handler)

# Boot setup
redis_conn = Redis(host=IzumiConf.redis_host, port=IzumiConf.redis_port, password=IzumiConf.redis_password)
notify_queue = Queue('notify', connection=redis_conn)
encode_queue = Queue('encode', connection=redis_conn)
encode_hp_queue = Queue('encode-hp', connection=redis_conn)
encode_mp_queue = Queue('encode-mp', connection=redis_conn)
encode_lp_queue = Queue('encode-lp', connection=redis_conn)

# Timeouts
JOB_TIMEOUT = "12h"
RESULT_TTL = "7d"
FAILURE_TTL = "7d"

app = Flask(__name__)
app.config['RQ_DASHBOARD_REDIS_URL'] = 'redis://:{password}@{host}:{port}'.format(
    host=IzumiConf.redis_host,
    port=str(IzumiConf.redis_port),
    password=IzumiConf.redis_password)
app.register_blueprint(rq_dashboard.blueprint, url_prefix=IzumiConf.dashboard_route)

# Disable the default Flask logging since RQ spams it and we want to use our own
logging.getLogger('werkzeug').setLevel(logging.ERROR)

@app.route(IzumiConf.notify_route, methods=['POST'])
def notify():

    LoggingUtils.info("Received a request for notify")

    authorized = RequestAuthorizer.authorize(request.headers)
    # Check authorization
    if not authorized:
        LoggingUtils.debug("Returning 401 http status code", color=LoggingUtils.YELLOW)
        return "Unauthorized request", 401

    job = JobGenerator.create_from_json(request.get_json())
    # Create a job instance
    if not job:
        LoggingUtils.debug("Returning 400 http status code", color=LoggingUtils.YELLOW)
        return "Malformed request", 400

    # Enqueue job
    notify_queue.enqueue(notify_worker, job, job_timeout=JOB_TIMEOUT, result_ttl=RESULT_TTL, failure_ttl=FAILURE_TTL, job_id=_create_job_id(job.episode, "notify"))
    LoggingUtils.info("Enqueued a new notify job to the 'notify' queue", color=LoggingUtils.CYAN)

    return "Request accepted", 200

@app.route(IzumiConf.encode_route, methods=['POST'])
def encode():

    LoggingUtils.info("Received a request under the default encode route")

    authorized = RequestAuthorizer.authorize(request.headers)
    # Check authorization
    if not authorized:
        LoggingUtils.debug("Returning 401 http status code", color=LoggingUtils.YELLOW)
        return "Unauthorized request", 401

    job = JobGenerator.create_from_json(request.get_json())
    # Create a job instance
    if not job:
        LoggingUtils.debug("Returning 400 http status code", color=LoggingUtils.YELLOW)
        return "Malformed request", 400

    # Enqueue job
    encode_queue.enqueue(encode_worker, job, job_timeout=JOB_TIMEOUT, result_ttl=RESULT_TTL, failure_ttl=FAILURE_TTL, job_id=_create_job_id(job.episode, "encode"))
    LoggingUtils.info("Enqueued a new encoder job to the 'encode' queue", color=LoggingUtils.CYAN)

    return "Request accepted", 200

# More encoding support, but for encoding priority queues

@app.route(IzumiConf.encode_hp_route, methods=['POST'])
def encode_hp():

    LoggingUtils.info("Received a request under the high priority encode route")

    authorized = RequestAuthorizer.authorize(request.headers)
    # Check authorization
    if not authorized:
        LoggingUtils.debug("Returning 401 http status code", color=LoggingUtils.YELLOW)
        return "Unauthorized request", 401

    job = JobGenerator.create_from_json(request.get_json())
    # Create a job instance
    if not job:
        LoggingUtils.debug("Returning 400 http status code", color=LoggingUtils.YELLOW)
        return "Malformed request", 400

    # Enqueue job
    encode_hp_queue.enqueue(encode_worker, job, job_timeout=JOB_TIMEOUT, result_ttl=RESULT_TTL, failure_ttl=FAILURE_TTL, job_id=_create_job_id(job.episode, "encode-hp"))
    LoggingUtils.info("Enqueued a new encoder job to the 'encode' queue", color=LoggingUtils.CYAN)

    return "Request accepted", 200

@app.route(IzumiConf.encode_mp_route, methods=['POST'])
def encode_mp():

    LoggingUtils.info("Received a request under the medium priority encode route")

    authorized = RequestAuthorizer.authorize(request.headers)
    # Check authorization
    if not authorized:
        LoggingUtils.debug("Returning 401 http status code", color=LoggingUtils.YELLOW)
        return "Unauthorized request", 401

    job = JobGenerator.create_from_json(request.get_json())
    # Create a job instance
    if not job:
        LoggingUtils.debug("Returning 400 http status code", color=LoggingUtils.YELLOW)
        return "Malformed request", 400

    # Enqueue job
    encode_mp_queue.enqueue(encode_worker, job, job_timeout=JOB_TIMEOUT, result_ttl=RESULT_TTL, failure_ttl=FAILURE_TTL, job_id=_create_job_id(job.episode, "encode-mp"))
    LoggingUtils.info("Enqueued a new encoder job to the 'encode' queue", color=LoggingUtils.CYAN)

    return "Request accepted", 200

@app.route(IzumiConf.encode_lp_route, methods=['POST'])
def encode_lp():

    LoggingUtils.info("Received a request under the low priority encode route")

    authorized = RequestAuthorizer.authorize(request.headers)
    # Check authorization
    if not authorized:
        LoggingUtils.debug("Returning 401 http status code", color=LoggingUtils.YELLOW)
        return "Unauthorized request", 401

    job = JobGenerator.create_from_json(request.get_json())
    # Create a job instance
    if not job:
        LoggingUtils.debug("Returning 400 http status code", color=LoggingUtils.YELLOW)
        return "Malformed request", 400

    # Enqueue job
    encode_lp_queue.enqueue(encode_worker, job, job_timeout=JOB_TIMEOUT, result_ttl=RESULT_TTL, failure_ttl=FAILURE_TTL, job_id=_create_job_id(job.episode, "encode-lp"))
    LoggingUtils.info("Enqueued a new encoder job to the 'encode' queue", color=LoggingUtils.CYAN)

    return "Request accepted", 200

@app.errorhandler(RedisConnectionError)
def handle_redis_connection_error(error):
    LoggingUtils.critical("It appears that Redis is down.")
    response = {
        "success": False,
        "error": {
            "type": "Redis Connection",
            "message": "Redis connection error has occured."
        }
    }
    return jsonify(response), 500

def _create_job_id(episode: str, jobtype: str) -> str:
    return "[{}] {}".format(episode, jobtype)

if __name__ == "__main__":

    LoggingUtils.info("Initializing Izumi application server")
    app.run(host='0.0.0.0', port=8080, debug=False)