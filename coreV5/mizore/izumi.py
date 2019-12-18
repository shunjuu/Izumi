"""
This is the application-level FLask server that handles all incoming requests.
"""

# Basic imports
import logging
import json
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
from src.encoder import worker as encode_worker

# Flask imports
from flask import Flask, jsonify, request

# Distributed System imports
import rq_dashboard
from redis import Redis
from rq import Queue

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

app = Flask(__name__)
app.config['RQ_DASHBOARD_REDIS_URL'] = 'redis://:{password}@{host}:{port}'.format(
    host=IzumiConf.redis_host,
    port=str(IzumiConf.redis_port),
    password=IzumiConf.redis_password)
app.register_blueprint(rq_dashboard.blueprint, url_prefix=IzumiConf.dashboard_route)

# Disable the default Flask logging since RQ spams it and we want to use our own
logging.getLogger('werkzeug').setLevel(logging.ERROR)

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
    Queue('encode', connection=redis_conn).enqueue(encode_worker.encode, job, job_timeout="4h", result_ttl="7d", failure_ttl="7d", job_id=job.episode)
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
    Queue('encode-hp', connection=redis_conn).enqueue(encode_worker.encode, job, job_timeout="4h", result_ttl="7d", failure_ttl="7d", job_id=job.episode)
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
    Queue('encode-mp', connection=redis_conn).enqueue(encode_worker.encode, job, job_timeout="4h", result_ttl="7d", failure_ttl="7d", job_id=job.episode)
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
    Queue('encode-lp', connection=redis_conn).enqueue(encode_worker.encode, job, job_timeout="4h", result_ttl="7d", failure_ttl="7d", job_id=job.episode)
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

if __name__ == "__main__":

    LoggingUtils.info("Initializing Izumi application server")
    app.run(host='0.0.0.0', port=8080, debug=False)