import sys
import os

import json
import pprint

from flask import Flask, request

from src.auth_handler import AuthHandler
from src.config_handler import ConfigHandler
from src.mochi_handler import MochiHandler
from src.network_handler import NetworkHandler
from src.print_handler import PrintHandler
from src.request_handler import RequestHandler

app = Flask(__name__)

c = (ConfigHandler() if 'DOCKER' not in os.environ or not bool(os.environ.get("DOCKER"))
    else ConfigHandler("/src/config.yml")) # Represents ConfigHandler
p = PrintHandler(c) # Represents PrintHandler
a = (AuthHandler(p) if 'DOCKER' not in os.environ or not bool(os.environ.get("DOCKER"))
    else AuthHandler(p, "/src/auth.yml")) # Represents AuthHandler
m = MochiHandler(c, p)

@app.route(c.route, methods=['POST'])
def mochi():

    try:
        a.refresh()
        status = a.authorize(request.headers)

        if not status:
            return "Unauthorized request", 401

        r = RequestHandler(request, p)
        if r.sub_type in c.mochi_sub_types:
            m.send(r)

            n = NetworkHandler(c, r, p)
            n.notify()

        return "Request accepted", 200
    except Exception as e:
        print(e)
        return "Error with request", 400

if __name__ == "__main__":

    app.run(host='0.0.0.0', port=c.listen_port)