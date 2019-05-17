import sys
import os

from src.prints.encode.h264_standard_prints import H264StandardPrints

ENCODE = "{} -i \"{}\" -vf subtitles=\"{}\" {} \"{}\""
# ffmpeg -i episode.mkv -vf subtitles="/path/to/episode.mkv" flags "out.mp4"

class H264Standard:
    """
    Representation of the standard H264 encoding the system does.
    This module is a stand-in until the smart-encoder is developed.
    """

    def __init__(self, conf, printh, src_file, end_folder, end_file):
        """
        Args:
            src: A path to a file that we will be sourcing from. 
                 This file should be called "temp.mkv"
            end: A path to a file that H264Standard will generate.
        """

        # Logging Tools
        self._logger = printh.logger
        self._prints = H264StandardPrints(printh.Colors())

        self._conf = conf
        self._src_file = src_file
        self._end_folder = end_folder if end_folder.endswith("/") else end_folder + "/"
        self._end_file = end_file

        self._ffmpeg_8bit = self._get_ffmpeg_8bit_calling_path()


    def encode(self):
        """
        Encode the file into the specified out path.
        """
        full_end_file = self._end_folder + self._end_file
        self._logger.warning(self._prints.ENCODE_START.format(self._end_file))
        
        os.system(ENCODE.format(
            self._ffmpeg_8bit,
            self._src_file, self._src_file,
            self._conf.encode_encode_flags,
            full_end_file))

        self._logger.warning(self._prints.ENCODE_FINISH.format(self._end_file))


    def _get_root_directory_calling_path(self):
        """
        Gets the directory of the wherever encoder.py was called from
        """
        path = os.path.abspath(os.path.dirname(sys.argv[0]))
        if not path.endswith("/"):
            path += "/"

        return path


    def _get_ffmpeg_8bit_calling_path(self):
        """
        Gets the calling path for the standard 8-bit ffmpeg
        """

        if 'DOCKER' in os.environ and bool(os.environ.get("DOCKER")):
            self._logger.info(self._prints.FFMPEG_8_PATH.format("/bin2/ffmpeg"))
            return "/bin2/ffmpeg"

        # Because of Docker build, just set it to the parent folder
        path = self._get_root_directory_calling_path() + "../bin/ffmpeg"
        self._logger.info(self._prints.FFMPEG_8_PATH.format(path))

        return path


    def _get_ffmpeg_10bit_calling_path(self):
        """
        Gets the calling path for the standard 8-bit ffmpeg
        """

        if 'DOCKER' in os.environ and bool(os.environ.get("DOCKER")):
            self._logger.info(self._prints.FFMPEG_8_PATH.format("/bin2/ffmpeg-10bit"))
            return "/bin2/ffmpeg-10bit"


        path = self._get_root_directory_calling_path() + "../bin/ffmpeg-10bit"
        self._logger.info(self._prints.FFMPEG_10_PATH.format(path))

        return path
