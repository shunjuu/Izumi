import sys
import os

import json
import yaml

import pprint as pp

import requests

# Print statements
from src.prints.auth_handler_prints import AuthHandlerPrints

# File Extension Definitions
YAML_EXT = ['.yaml', '.yml']
JSON_EXT = ['.json']

class AuthHandler:
    """
    AuthHandler deals with authorizing incoming requests.
    """

    def __init__(self, printh, apath="auth.yml"):
        """
        Args:
            apath - A path that points to the authorization file. 
            If not specified, it will default to auth.yml
        """

        # Logging - this needs to be before all other methods are initailized
        self._logger = printh.logger
        self._prints = AuthHandlerPrints(printh.Colors())

        # Get the absolute path for all use cases
        self._apath = os.path.abspath(apath)
        # Load the initial file into a dict
        initial_auth = self._load_local_auth(self._apath)
        # If the inital auth is empty, initialize it to an empty dict
        self._auth_entries = initial_auth if initial_auth else dict()



    def refresh(self):
        """
        This refreshes the current variables with the new config.
        """
        # Fetch the apath and update it again
        self._logger.info(self._prints.AUTH_REFRESH)
        refresh_auth = self._load_local_auth(self._apath)
        if refresh_auth:
            self._auth_entries = refresh_auth
            self._logger.info(self._prints.AUTH_REFRESH_SUCCESS.format(self._apath))
        else:
            self._auth_entries = dict()
            self._logger.info(self._prints.AUTH_REFRESH_SUCCESS.format("an empty dict"))


    def _load_local_auth(self, apath_abs):
        """
        Loads the auth path into a parasable dict.

        ArgS:
            apath_abs: The absolute path of the auth file, path only

        Returns: A dict representation of the config file
        """

        # Determine if we're loading a YAML or JSON file

        _, file_ext = os.path.splitext(apath_abs)

        if file_ext in YAML_EXT:
            with open(apath_abs, 'r') as atyml:
                try:
                    auth = yaml.full_load(atyml)
                    self._logger.info(self._prints.LOCAL_AUTH_YAML_SUCCESS.format(apath_abs))
                    return auth
                except:
                    self._logger.error(self._prints.LOCAL_AUTH_YAML_ERROR.format(apath_abs))
                    raise Exception()

        elif file_ext in JSON_EXT:
            with open(apath_abs, 'r') as atjson:
                try:
                    auth = json.load(atjson)
                    self._logger.info(self._prints.LOCAL_AUTH_JSON_SUCCESS.format(apath_abs))
                    return auth
                except:
                    self._logger.error(self._prints.LOCAL_AUTH_JSON_ERROR.format(apath_abs))
                    raise Exception()

        # If we've reached this point, then print some 
        self._logger.error(self._prints.AUTH_FAILURE_NO_JSON_OR_YAML)
        raise Exception()

    def authorize(self, headers):
        """
        Detremines if the auth_key is accepted or not.

        Params:
            auth_key: A string that is the auth key embedded in the request.

        Returns: A boolean indicating whether or not request is accepted
        """

        # Attempt to get a key embedded within the request
        key = headers.get("Authorization")

        # If no authorization was provided, check if this instance is
        # using any keys
        if not key:
            # Check if auth_entries has zero entries
            if not self._auth_entries:
                self._logger.warning(self._prints.AUTH_SUCCESS_NO_ENTRIES_NO_KEY)
                return True
            else:
                self._logger.warning(self._prints.AUTH_FAILURE_YES_ENTRIES_NO_KEY)
                return False

        else:
            # In the event that the request contains an auth_key
            # but the instance does not have any registered,
            # still return false
            if not self._auth_entries:
                self._logger.warning(self._prints.AUTH_FAILURE_NO_ENTRIES_YES_KEY)
                return False

            # An authorization key was provided
            for group, group_key in self._auth_entries.items():

                if key == group_key:
                    # A match was found, return true
                    self._logger.warning(self._prints.AUTH_SUCCESS_YES_ENTRIES_YES_KEY) 
                    return True

        # No matches were found, return false
        self._logger.warning(self._prints.AUTH_FAILURE_YES_ENTRIES_NO_MATCH)
        return False