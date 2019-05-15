import sys
import os

import pprint as pp 
import requests


from src.prints.network_handler_prints import NetworkHandlerPrints

class NetworkHandler:
    """
    NetworkHandler will handle sending out all of the various requests to
    multiple endpoints and platforms.

    All requests sent out in v4.0 should follow the exact same structure; hence,
    NetworkHandler is designed to do so. This module may be replicated in other
    Units if designated necessary.
    """

    def __init__(self, conf, fileh, printh):
        """
        Args:
            conf - a ConfigHandler that should already be populated
            fileh - a FileHandler that should already be populated

            NetworkHandler should generate the request upon instantialization.

            Request type json:
            {
                "show": $SHOW_NAME,
                "episode": $EPISODE_NAME,
                "filesize" : $FILE_SIZE,
                "sub": $SUB_TYPE,
                "duration": TODO (lol)
            }
        """

        # Store handlers as "private" variables
        self._conf = conf
        self._fileh = fileh

        # Logging Tools
        self._logger = printh.get_logger()
        self._prints = NetworkHandlerPrints(printh.Colors())

        # Variables
        self.request = self._generate_request(fileh) # A dict representing the JSOn request


    def _generate_request(self, fileh):
        """
        Generates the request for Requests to send using properties found
        by fileh.

        Params:
            fileh: A filehandler object that is already populated

        Returns: The request JSON as a dict object
        """
        req = dict()
        req['show'] = fileh.show_clean
        req['episode'] = fileh.episode_new
        req['filesize'] = fileh.filesize
        req['sub'] = fileh.sub_type

        """
        We'll be ignoring the signature body for now, and duration 
        can be handled later.`
        """

        return req

    def _send_request(self, url, auth_key=None):
        """
        Helper function that sends the existing request out to a URL.
        Ensures that the repsonse code is a 2XX code or else raises an exception.

        Params:
            url: The url to send the request ot
            auth_key: An optional authorization header key

        Returns:
            True if request was successful and in 2XX range
            False if an error occured when sending request or out of 2XX
        """
        headers = dict()
        headers['Content-Type'] = "application/json"
        if auth_key:
            # Legacy clients may not support one or the other (caps)
            headers['Authorization'] = auth_key
            headers['authorization'] = auth_key

        try:
            self._logger.info(self._prints.SENDING_REQUEST.format(url))
            res = requests.post(url, json=self.request, headers=headers, timeout=5)
        except requests.exceptions.ConnectionError:
            # When the internet has some kind of issue, just exit
            self._logger.warning(self._prints.SENDING_REQUEST_CONNECTION_ERROR) 
            return False
        except requests.exceptions.MissingSchema:
            # When http or https is missing
            self._logger.warning(self._prints.SENDING_REQUEST_SCHEMA_ERROR.format(url))
            return False
        except request.exceptions.Timeout:
            # When the connection times out
            self._logger.warning(self._prints.SENDING_REQUEST_TIMEOUT_ERROR.format(url))
            return False
        except:
            self._logger.warning(self._prints.SENDING_REQUEST_FAIL.format(url))
            return False

        # Validate that the response header was within a 2XX
        if 200 > res.status_code or res.status_code >= 300:
            self._logger.info(self._prints.SENDING_REQUEST_BAD_CODE.format(
                url, res.status_code))
            return False

        self._logger.info(self._prints.SENDING_REQUEST_SUCCESS.format(url))
        return True


    def _notify(self, always, sequential):
        """
        A general form to send out requests and get responses.
        Yes, this is a higher-order function.

        Params:
            always: A list of "Always" formatted entries
            sequential: A dict of "Sequential" formatted entires
        """

        # First, send out the requests to the always entries

        self._logger.info(self._prints.BODY_ALWAYS)

        for entry in always: 
            # Try to send with auth key, but if it doesn't have it send without
            try:
                self._send_request(entry['url'], entry['auth'])
            except:
                self._send_request(entry['url'])

        # Second, keep trying the sequential until one is successful

        self._logger.info(self._prints.BODY_SEQUENTIAL)

        # There are multiple groupings also supported
        for _, group in sequential.items():
            for entry in group:
                # Try to send with auth key, but if it doensn't have it send without
                try:
                    if self._send_request(entry['url'], entry['auth']):
                        break
                except:
                    if self._send_request(entry['url']):
                        break 

        return

    # Public functions for telling NH to send out notifications.

    def notify_encoders(self):
        """
        Sends out notifications to all the U2 Encoders per their standards.
        """

        self._logger.info(self._prints.GROUP_ENCODERS)

        # Call the general notifier, passing in the encoder functions
        self._notify(self._conf.get_encoders_always(), 
                        self._conf.get_encoders_sequential())

    def notify_notifiers(self):
        """
        Sends out notifications to all the U3 Notifier modules
        """

        self._logger.info(self._prints.GROUP_NOTIFIERS)

        # Call the general notifer, passing in the notifier functions
        self._notify(self._conf.get_notifiers_always(),
                        self._conf.get_notifiers_sequential())

    def notify_distributors(self):
        """
        Sends out notifications to all the U4 Distributor modules
        """

        self._logger.info(self._prints.GROUP_DISTRIBUTORS)

        # Call the general notifier, passing in the distributor functions
        self._notify(self._conf.get_distributors_always(),
                        self._conf.get_distributors_sequential())
