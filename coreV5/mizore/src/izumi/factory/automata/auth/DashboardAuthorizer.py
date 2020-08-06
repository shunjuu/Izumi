#pylint: disable=import-error

from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils
from src.shared.factory.utils.LoggingUtils import LoggingUtils

from flask import request, Response

# Logging is temporarily disabled because Dashboard makes a lot of requests
class DashboardAuthorizer:

    _CONF = ConfLoaderUtils.get_dashboard_auth()

    @classmethod
    def authorize(cls) -> bool:
        if not cls._CONF:
            return
        auth = request.authorization
        if not auth or not cls.check_auth(auth.username, auth.password):
            return Response(
                'Unauthorized access to this URL.\n'
                'Please login with proper credentials', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'})

    @classmethod
    def check_auth(cls, username, password):
        return username in cls._CONF and \
                password == cls._CONF[username]
