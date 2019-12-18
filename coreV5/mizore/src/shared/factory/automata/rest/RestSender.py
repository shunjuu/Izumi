"""
Handles sending the rest-based notification requests

Requests take the form:

{
    "show": $SHOW_NAME,
    "episode": $EPISODE_NAME,
    "filesize": $FILE_SIZE,
    "sub": $SUB_TYPE
}
"""

import requests

from typing import Dict, List

from src.shared.factory.utils.LoggingUtils import LoggingUtils #pylint: disable=import-error

class RestSender:

    @staticmethod
    def send(json_str: str, urls: List[Dict[str, str]]) -> bool:
        """
        Sends notifications. Returns bool if all successful
        Assumes the passed in string is already in JSON form.
        """
        for url in urls:

            LoggingUtils.info("Sending request to url {}".format(url['url']))

            headers = dict()
            headers['Content-Type'] = "application/json"

            if 'auth' in url and url['auth']:
                headers['Authorization'] = url['auth']
                headers['authorization'] = url['auth']
            
            try:
                res = requests.post(url['url'], json=json_str, headers=headers, timeout=5)

                if res.status_code == 200:
                    LoggingUtils.info("Successfully sent with return of 200 OK")
                elif res.status_code == 201:
                    LoggingUtils.info("Successfully sent with return of 201 Created")
                elif res.status_code == 202:
                    LoggingUtils.info("Successfully sent with return of 202 Accepted")
                else:
                    LoggingUtils.info("Sent request with a return of {}".format(res.status_code))

            except requests.exceptions.ConnectionError:
                LoggingUtils.warning("Connection error occured while sending to {}".format(url['url']), color=LoggingUtils.RED)
            except requests.exceptions.MissingSchema:
                LoggingUtils.warning("Missing http/https schema for {}".format(url['url']), color=LoggingUtils.RED)
            except requests.exceptions.Timeout:
                LoggingUtils.warning("Timeout occured while sending to {}".format(url['url']), color=LoggingUtils.RED)
            except:
                LoggingUtils.warning("Unknown error occured while sending to {}".format(url['url']), color=LoggingUtils.RED)
            
        return True
