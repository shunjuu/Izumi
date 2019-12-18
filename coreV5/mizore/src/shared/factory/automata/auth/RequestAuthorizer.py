"""
Handles validating whether or not an incoming request is sufficiently authorized

TODO: Functionality that wasn't copied over:
- Pass in path to custom auth file
- Refresh on call
- JSON auth file
"""

from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils #pylint: disable=import-error
from src.shared.factory.utils.LoggingUtils import LoggingUtils #pylint: disable=import-error

from werkzeug.datastructures import EnvironHeaders

class RequestAuthorizer:

    _CONF = ConfLoaderUtils.get_auth()

    @classmethod
    def authorize(cls, headers: EnvironHeaders) -> bool:

        key = headers.get("Authorization")

        # If incoming request did not provide a key
        if not key:
            # Case where no key provided when one was required
            if cls._CONF:
                LoggingUtils.info("Request denied - a key was required but no key was provided", color=LoggingUtils.YELLOW)
                return False
            # Case where no key was provided and none were required
            elif not cls._CONF:
                LoggingUtils.info("Request authorized - no key was required, and no key was provided", color=LoggingUtils.GREEN)
                return True
        
        else:
            # Case where a key was provided and one was required
            if cls._CONF:
                for user, password in cls._CONF.items():
                    if key == password:
                        # Found a matching key, so return True
                        LoggingUtils.info("Request authorized - a key was required, and a matching key was provided", color=LoggingUtils.GREEN)
                        LoggingUtils.info("Matching key was sent from {}".format(user))
                        return True
            
                # If no matching key was found, return false
                LoggingUtils.info("Request denied - a key was required, but a nonmatching key was provided", color=LoggingUtils.YELLOW)
            # Case where a key was provided but one was not required
            elif not cls._CONF:
                LoggingUtils.info("Request denied - a key was not required, but one was provided", color=LoggingUtils.YELLOW)
                return False
        
