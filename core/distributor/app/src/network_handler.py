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

    This module is not a replica of   
    """

    def __init__(self, conf, reqh, printh):
        """
        Args:
            conf - a ConfigHandler that should already be populated
            reqh - a RequestHandler from the incoming request

            NetworkHandler should generate the request upon instantialization.

            Request type json:
           
                "show": $SHOW_NAME,
                "episode": $EPISODE_NAME,
                "filesize" : $FILE_SIZE,
                "sub": $SUB_TYPE,
                "duration": TODO (lol)
            }

            In this case, NetworkHandler just imports from RequestHandler
        """

        # Store handlers as "private" variables
        self._conf = conf
        self._reqh = reqh

        # Logging Tools
        self._logger = printh.logger
        self._prints = NetworkHandlerPrints(printh.Colors())

        # Variables
        self._request = self._generate_request(self._reqh) # A dict representing the JSOn request


    def _generate_request(self, reqh):
        """
        Generates the request for Requests to send using properties found
        by reqh.

        Params:
            reqh: A requesthandler object that is already populated

        Returns: The request JSON as a dict object
        """
        req = dict()
        req['show'] = reqh.show
        req['episode'] = reqh.episode
        req['filesize'] = reqh.filesize
        req['sub'] = reqh.sub_type

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
            url: The url to send the request to
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
            res = requests.post(url, json=self._request, headers=headers, timeout=5)
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
    
    def notify(self):
        """
        Sends out notifcations to all the Endpoints
        """
        self._logger.info(self._prints.ENDPOINT_START)
        self._notify(self._conf.endpoints_always, self._conf.endpoints_sequential)