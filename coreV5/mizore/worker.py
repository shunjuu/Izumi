"""
This script is for running workers. We use this to pre-load all binaries we need.
"""

import getpass
import os
import platform
import signal
import socket
import sys

from datetime import datetime

from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from redis.exceptions import TimeoutError
#from rq import Connection, Queue, Worker
from src.rq.rq import Connection, Queue, Worker

from src.izumi.factory.conf.IzumiConf import IzumiConf
from src.shared.exceptions.errors.WorkerCancelledError import WorkerCancelledError
from src.shared.factory.utils.LoggingUtils import LoggingUtils

# Preload libraries
from src.encoder import worker as encode_worker

# Reject Mac OS systems
#if platform.system().lower() == "darwin":
#    print("Warning: MacOS has an ObjC error with RQ, please run 'rq worker <queue> instead'")
#    sys.exit()

# Set worker name based on user host, or if Docker, the passed in build variable
WORKER_NAME = str()
if 'WORKER_NAME' in os.environ:
    WORKER_NAME = "{}|docker".format(os.environ.get('WORKER_NAME'))
else:
    WORKER_NAME = "{name}@{fqdn}:{ident}".format(name=getpass.getuser(),
                                                    fqdn=socket.getfqdn(),
                                                    ident=datetime.now().strftime("%Y%m%d.%H%M"))
print("Set Worker name as {}".format(WORKER_NAME))

while True:
    with Connection():
        try:
            redis_conn = Redis(host=IzumiConf.redis_host,
                                port=IzumiConf.redis_port,
                                password=IzumiConf.redis_password,
                                socket_keepalive=True,
                                socket_timeout=180,
                                health_check_interval=60)

            qs = sys.argv[1:]
            w = Worker(qs, connection=redis_conn, name=WORKER_NAME)
            w.work()
        except RedisConnectionError as rce:
            LoggingUtils.critical("Lost connection to Redis instance, shutting down.", color=LoggingUtils.LRED)
            sys.exit()
        except WorkerCancelledError:
            LoggingUtils.warning("Worker killed externally, shutting down...")
            sys.exit()
        except TimeoutError:
            # We expect a timeout error to occur as this forces the worker to reregister
            # Silently handle and let the loop continue
            LoggingUtils.debug("Timeout error caught, handling silently...")
            pass