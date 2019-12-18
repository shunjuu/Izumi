"""
Helps determine whether or not Docker the application is in Docker mode
"""

from astropy.utils.decorators import classproperty
from os import environ

from src.shared.factory.utils.PathUtils import PathUtils #pylint: disable=import-error

class DockerUtils:

    _PATH = "/izumi/"
    _BIN = _PATH + "bin/"
    _CONF = _PATH + "conf/"

    _DOCKER = False
    if 'DOCKER' in environ and environ.get('DOCKER'):
        _DOCKER = True

    #pylint: disable=no-self-argument
    @classproperty
    def docker(cls) -> bool:
        return cls._DOCKER

    #pylint: disable=no-self-argument
    @classproperty
    def path(cls) -> str:
        """Returns root path of project when in Docker"""
        return PathUtils.clean_directory_path(cls._PATH)

    #pylint: disable=no-self-argument
    @classproperty
    def bin(cls) -> str:
        """Returns the bin path in Docker"""
        return PathUtils.clean_directory_path(cls._BIN)

    #pylint: disable=no-self-argument
    @classproperty
    def conf(cls) -> str:
        """Returns the conf path in Docker"""
        return PathUtils.clean_directory_path(cls._CONF)