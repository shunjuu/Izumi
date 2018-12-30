import sys
import os

import yaml

class Config():

    def __init__(self):
        with open("config.yml", 'r') as c:
            self.conf = yaml.load(c)
        
        # Set members

    def getList(self):
        return self.conf

