"""
Handles getting bin/executable paths
"""
from astropy.utils.decorators import classproperty

from src.shared.factory.utils.DockerUtils import DockerUtils #pylint: disable=import-error

class BinUtils:

    #pylint: disable=no-self-argument
    @classproperty
    def rclone(cls) -> str:

        if DockerUtils.docker:
            return DockerUtils.bin + "rclone"
        else:
            return "rclone"
    
    #pylint: disable=no-self-argument
    @classproperty
    def ffprobe(cls) -> str:

        if DockerUtils.docker:
            return DockerUtils.bin + "ffprobe"
        else:
            return "ffprobe"

    #pylint: disable=no-self-argument
    @classproperty
    def ffmpeg(cls) -> str:

        if DockerUtils.docker:
            return DockerUtils.bin + "ffmpeg"
        else:
            return "ffmpeg"
        
    #pylint: disable=no-self-argument
    @classproperty
    def ffmpeg10(cls) -> str:
        """Legacy function, because ffmpeg is multilib now"""
        if DockerUtils.docker:
            return DockerUtils.bin + "ffmpeg"
        else:
            return "ffmpeg"