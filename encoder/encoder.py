"""
U2 Encoder handles encoding new episodes recently uploaded.
"""

import sys
import os

import json
import yaml

from flask import Flask, request

from src.config_handler import ConfigHandler
from src.auth_handler import AuthHandler

# Let flask just use the default name
app = Flask(__name__)

c = ConfigHandler()
a = AuthHandler()


@app.route("/encode", methods=['POST'])
def encode():

    a.refresh()
    status = a.authorize(request.headers)

    return str(status), 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=c.get_listen_port())