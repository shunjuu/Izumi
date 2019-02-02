import sys
import os

ENCODE = "{} -i \"{}\" -vf subtitles=\"{}\" {} \"{}\""
# ffmpeg -i episode.mkv -vf subtitles="/path/to/episode.mkv" flags "out.mp4"

class H264Standard:
    """
    Representation of the standard H264 encoding the system does.
    This module is a stand-in until the smart-encoder is developed.
    """

    def __init__(self, conf, src_file, end_folder, end_file):
        """
        Args:
            src: A path to a file that we will be sourcing from. 
                 This file should be called "temp.mkv"
            end: A path to a file that H264Standard will generate.
        """

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
        os.system(ENCODE.format(
            self._ffmpeg_8bit,
            self._src_file, self._src_file,
            self._conf.get_encode_encode_flags(),
            full_end_file))


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

        path = self._get_root_directory_calling_path() + "bin/ffmpeg"

        return path


    def _get_ffmpeg_10bit_calling_path(self):
        """
        Gets the calling path for the standard 8-bit ffmpeg
        """

        path = self._get_root_directory_calling_path() + "bin/ffmpeg-10bit"

        return path