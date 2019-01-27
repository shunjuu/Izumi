"""
U2 Encoder handles encoding new episodes recently uploaded.
"""

import sys
import os

import json
import yaml

from flask import Flask, request

from src.config_handler import ConfigHandler

# Let flask just use the default name
app = Flask(__name__)

c = ConfigHandler()
print(c.get_logging_datefmt())

