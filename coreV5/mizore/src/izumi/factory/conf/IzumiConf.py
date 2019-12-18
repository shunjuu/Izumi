"""
Handles storing configurations for Izumi files. These are READONLY properties.
"""

from astropy.utils.decorators import classproperty

from src.shared.factory.utils.ConfLoaderUtils import ConfLoaderUtils #pylint: disable=import-error
from src.shared.factory.utils.PathUtils import PathUtils #pylint: disable=import-error

class IzumiConf:

    _CONF = ConfLoaderUtils.get_izumi()

    """
    Flask Properties
    """

    #pylint: disable=no-self-argument
    @classproperty
    def flask_port(cls) -> int:
        return int(cls._CONF['flask']['port'])

    """
    Flask Route Properties
    """

    #pylint: disable=no-self-argument
    @classproperty
    def dashboard_route(cls) -> str:
        return PathUtils.modify_flask_route(str(cls._CONF['flask']['routes']['dashboard']))

    #pylint: disable=no-self-argument
    @classproperty
    def distribute_route(cls) -> str:
        return PathUtils.modify_flask_route(str(cls._CONF['flask']['routes']['distribute']))

    #pylint: disable=no-self-argument
    @classproperty
    def encode_route(cls) -> str:
        return PathUtils.modify_flask_route(str(cls._CONF['flask']['routes']['encode']))

    #pylint: disable=no-self-argument
    @classproperty
    def modify_route(cls) -> str:
        return PathUtils.modify_flask_route(str(cls._CONF['flask']['routes']['modify']))

    #pylint: disable=no-self-argument
    @classproperty
    def notify_route(cls) -> str:
        return PathUtils.modify_flask_route(str(cls._CONF['flask']['routes']['encode']))

    """
    Encoding priorities
    """
    #pylint: disable=no-self-argument
    @classproperty
    def encode_hp_route(cls) -> str:
        return PathUtils.modify_flask_route(str(cls._CONF['flask']['routes']['encode_hp']))

    #pylint: disable=no-self-argument
    @classproperty
    def encode_mp_route(cls) -> str:
        return PathUtils.modify_flask_route(str(cls._CONF['flask']['routes']['encode_mp']))

    #pylint: disable=no-self-argument
    @classproperty
    def encode_lp_route(cls) -> str:
        return PathUtils.modify_flask_route(str(cls._CONF['flask']['routes']['encode_lp']))

    """
    Redis Properties
    """

    #pylint: disable=no-self-argument
    @classproperty
    def redis_host(cls) -> str:
        return str(cls._CONF['redis']['host'])

    #pylint: disable=no-self-argument
    @classproperty
    def redis_port(cls) -> int:
        return int(cls._CONF['redis']['port'])

    #pylint: disable=no-self-argument
    @classproperty
    def redis_password(cls) -> str:
        return str(cls._CONF['redis']['password'])

    """
    System Properties
    """

    #pylint: disable=no-self-argument
    @classproperty
    def system_name(cls) -> str:
        return str(cls._CONF['system']['name'])