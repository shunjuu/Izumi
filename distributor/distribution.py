"""
U4 Distribution handles distributing new episodes recently uploaded.
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

# For spawning background threads to distribute
from threading import Thread
from queue import Queue

from src.config_handler import ConfigHandler

app = Flask(__name__)

episode_job_queue = Queue()

c = ConfigHandler()

