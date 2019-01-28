import sys
import os

import json

import pprint as pp

from flask import request

SUB_TYPES = ['Hardsub', 'Softsub', 'None']

class RequestHandler:
    """
    Parses requests and gets their data for encoder to use.
    """

    def __init__(self, req):
        """
        Args: None.
        """

        # Store the various attributes of the current request
        self.show = None # The name of the show (not the episode)
        self.episode = None # The name of the episode
        self.filesize = None # The size of the file
        self.sub_type = None # The subtitle type 
        # No signature body will be processed

        rjson = req.get_json()

        self.show = self._load_show(rjson)
        self.episode = self._load_episode(rjson)
        self.filesize = self._load_filesize(rjson)
        self.sub_type = self._load_sub_type(rjson)

    def clear(self):
        """
        Clears the current variables.
        """
        self.show = None
        self.episode = None 
        self.filesize = None
        self.sub_type = None

    def _load_show(self, rjson):
        """
        Loads the name of the show embedded in the request.

        Params:
            rjson: The json in the body of the request

        Returns: The show name, as a string in the request
        """

        return rjson['show']

    def _load_episode(self, rjson):
        """
        Loads the name of the episode embedded in the request

        Params:
            rjson: The json in the body of the request

        Returns: The episode name as a string
        """

        return rjson['episode']

    def _load_filesize(self, rjson):
        """
        Loads the filesize embedded in the request

        Params:
            rjson: The json in the body of the request

        Returns: The filesize as an integer
        """

        # Wrap the rjson as an integer just in case
        # Other applications may get filesizes may have overflow
        # and prefer to use strings instead.
        return int(rjson['filesize'])

    def _load_sub_type(self, rjson):
        """
        Loads the sub type embedded in the request

        Params: 
            rjson: The json in the body of the request

        Returns: The sub type as a string
        """

        sub_type = rjson['sub']
        # Verify the sub type is correct

        if sub_type not in SUB_TYPES:
            # there is an error here
            sys.exit(2)

        return sub_type

    # Getter methods

    def get_show(self):
        """
        Returns the show of the request as a string
        """
        return self.show

    def get_episode(self):
        """
        Returns the episode of the request as a string
        """
        return self.episode

    def get_filesize(self):
        """
        Returns the filesize in the request as an int
        """
        return self.filesize

    def get_sub_type(self):
        """
        Returns the sub type as a string
        """
        return self.sub_type
