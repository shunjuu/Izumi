"""
Util class for acessing util files
"""

from astropy.utils.decorators import classproperty

from src.shared.factory.utils.DockerUtils import DockerUtils #pylint: disable=import-error
from src.shared.factory.utils.PathUtils import PathUtils #pylint: disable=import-error

class AssetUtils:

    _OPENSANS_PATH = "src/encoder/assets/OpenSans-Semibold.ttf"

    #pylint: disable=no-self-argument
    @classproperty
    def opensans_semibold(cls) -> str:

        if DockerUtils.docker:
            return PathUtils.clean_directory_path(DockerUtils.path) + cls._OPENSANS_PATH
        else:
            return PathUtils.abspath(cls._OPENSANS_PATH)