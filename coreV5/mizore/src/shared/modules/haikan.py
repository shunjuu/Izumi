import json
import pprint
import subprocess
import sys

from os import environ
from os.path import abspath
from typing import List

from src.shared.factory.utils.BinUtils import BinUtils #pylint: disable=import-error
from src.shared.factory.utils.LoggingUtils import LoggingUtils #pylint: disable=import-error

class Haikan:

    # Same commands, but use local ffprobe for interactive - because Mac/Linux builds differ
    _FFPROBE = (BinUtils.ffprobe, "-print_format", "json", "-show_format", "-v", "quiet",
        "-show_format", "-show_streams", "-i")

    class ProbeInfo:
        """
        Inner class to store information retrieved by the Probe
        """
        def __init__(self):
            
            # There are no setters because ProbeInfo is defined in Haikan
            # Internal methods can access private members by choice

            # Basic Information
            self._filename: str = str()
            self._bitrate: int = int()
            self._duration: float = float()
            self._size: int = int()
            self._streams: int = int()

            # Stream information

            # We can assume there's only one video stream
            self._video_codec_name: str = str()
            self._video_codec_long_name: str = str()
            self._video_stream_index: int = int()

            # There may be multiple audio streams
            # We only want the one in JP with the highest quality
            self._audio_codec_name: str = str()
            self._audio_codec_long_name: str = str()
            self._audio_stream_index: int = int()
            self._audio_tags_language: str = str()

            # There may be a regular subtitle stream and a signs/songs
            # Report both if they exist, must be in ENglish
            self._subtitle_main_index: int = int()
            self._subtitle_extra_index: int = -1 # -1 to indicate not existing

        @property
        def filename(self): return self._filename
        @property
        def bitrate(self) -> str: return self._bitrate
        @property
        def duration(self) -> float: return self._duration
        @property
        def size(self) -> int: return self._size
        @property
        def streams(self) -> int: return self._streams

        @property
        def video_bits(self) -> int: return self._video_bits_per_raw_sample
        @property
        def video_codec_name(self) -> str: return self._video_codec_name
        @property
        def video_codec_long_name(self) -> str: return self._video_codec_long_name
        @property
        def video_stream_index(self) -> int: return self._video_stream_index
        
        @property            
        def audio_codec_name(self) -> str: return self._audio_codec_name
        @property
        def audio_codec_long_name(self) -> str: return self._audio_codec_long_name
        @property
        def audio_stream_index(self) -> int: return self._audio_stream_index
        @property
        def audio_tags_language(self) -> str: return self._audio_tags_language
        
        @property
        def subtitle_main_index(self) -> int: return self._subtitle_main_index
        @property
        def subtitle_extra_index(self) -> int: return self._subtitle_extra_index

    @classmethod
    def _set_audio_info(cls, pi, stream):
        pi._audio_stream_index = int(stream['index'])
        pi._audio_codec_name = str(stream['codec_name']).lower()
        pi._audio_codec_long_name = stream['codec_long_name']
        pi._audio_tags_language = str(stream['tags']['language']).lower()

    @classmethod
    def _load_audio_info(cls, pi, info):
        """
        Method to load proper Japanese audio stream data into ProbeInfo

        Preferred order of audio tracks:
        FLAC >> MP3 >> AAC. All else is no good
        TODO: Handle Commentary streams
        """
        # If there's only one audio stream, load that - regardless of what it is
        # If there are multiple tracks, load in order of preference, but if no tags - don't load any
        streams = info['streams']
        audio_stream_count = 0

        for stream in streams:
            if stream['codec_type'].lower() == "audio":
                audio_stream_count += 1

        if audio_stream_count == 1:
            # There is only one stream, pull its data
            for stream in streams:
                if stream['codec_type'].lower() == "audio":
                    pi._audio_stream_index = int(stream['index'])
                    pi._audio_codec_name = str(stream['codec_name']).lower()
                    pi._audio_codec_long_name = stream['codec_long_name']

                    if 'tags' in stream and 'language' in stream['tags']:
                        pi._audio_tags_language = str(stream['tags']['language']).lower()
                    break
        else:
            for stream in streams:
                if stream['codec_type'].lower() == "audio":
                    if 'tags' in stream:
                        if 'language' in stream['tags']:
                            lang = str(stream['tags']['language']).lower()
                            if lang == "jpn" or lang == "jp":
                                if stream['codec_name'] == "flac":
                                    cls._set_audio_info(pi, stream)
                                elif stream['codec_name'] == "mp3" or stream['codec_name'] == "aac":
                                    if pi._audio_codec_name != "flac":
                                        cls._set_audio_info(pi, stream)
                                else:
                                    if pi._audio_codec_name != "flac" and pi._audio_codec_name != "mp3" and pi._audio_codec_name != "aac":
                                        cls._set_audio_info(pi, stream)
            # All streams iterated but none were Japanese - this means the streams aren't tagged properly.
            # In this case, do not set anything - This will be a signal that the audio streams aren't reliable

            # However, for now, we should just set the first stream anyways and log a warning
            if not pi.audio_codec_name:
                LoggingUtils.warning("Unable to determine which audio stream to index, using first available...", color=LoggingUtils.RED)
                for stream in streams:
                    if stream['codec_type'].lower() == "audio":
                        pi._audio_stream_index = int(stream['index'])
                        pi._audio_codec_name = str(stream['codec_name']).lower()
                        pi._audio_codec_long_name = stream['codec_long_name']

                        if 'tags' in stream and 'language' in stream['tags']:
                            pi._audio_tags_language = str(stream['tags']['language']).lower()
                        break
            else:
                LoggingUtils.debug("Audio stream index was set in multiselect, proceeding...")

    @classmethod
    def _load_video_info(cls, pi, info):
        """
        Method to load video info. As a general rule, we can assume there's only one video track.
        """
        streams = info['streams']
        for stream in streams:
            if stream['codec_type'].lower() == "video":
                pi._video_codec_name = str(stream['codec_name']).lower()
                pi._video_codec_long_name = stream['codec_long_name']
                pi._video_stream_index = int(stream['index'])
    
    @classmethod
    def _load_subtitle_info(cls, pi, info):

        streams = info['streams']
        subtitle_stream_count = 0
        for stream in streams:
            if stream['codec_type'].lower() == "subtitle":
                subtitle_stream_count += 1
        
        if subtitle_stream_count == 1:
            for stream in streams:
                if stream['codec_type'].lower() == "subtitle":
                    pi._subtitle_main_index = int(stream['index'])
                    break
        else:
            for stream in streams:
                if stream['codec_type'].lower() == "subtitle":
                    if 'tags' in stream:
                        if 'language' in stream['tags']:
                            language = stream['tags']['language']
                            if "eng" in language.lower():
                                LoggingUtils.debug("Set main subtitle index based on language detection")
                                pi._subtitle_main_index = int(stream['index'])
                        elif 'title' in stream['tags']:
                            title = stream['tags']['title']
                            if title.lower() == "english":
                                LoggingUtils.debug("Set main subtitle index based on title detection")
                                pi._subtitle_main_index = int(stream['index'])
                            # Set the OP/ED/Signs track
                            elif ("op" in title.lower() and "ed" in title.lower()) or "sign" in title.lower():
                                LoggingUtils.debug("Set secondary subtitle index based on title detection")
                                pi._subtitle_extra_index = int(stream['index'])
            # If no subs were selected, default to the first available
            if pi.subtitle_main_index < 1:
                LoggingUtils.warning("Unable to determine which subtitle stream to index, using first available...", color=LoggingUtils.RED)
                for stream in streams:
                    if stream['codec_type'].lower() == "subtitle":
                        pi._subtitle_main_index = int(stream['index'])
                        break
            else:
                LoggingUtils.debug("Subtitle stream was detected in multiselected, proceeding...")

    @classmethod
    def _make_probe_info(cls, info):

        pi = Haikan.ProbeInfo()

        # Load format data first
        fmt = info['format']
        pi._filename = str(fmt['filename'])
        pi._bitrate = int(fmt['bit_rate'])
        pi._duration = float(fmt['duration'])
        pi._size = int(fmt['size'])
        pi._streams = int(fmt['nb_streams'])

        cls._load_audio_info(pi, info)
        cls._load_video_info(pi, info)
        cls._load_subtitle_info(pi, info)

        return pi

    @classmethod
    def scan(cls, path):
        """
        Scans a video file, given a path
        """

        a_path = abspath(path)

        sys_command = list(cls._FFPROBE)
        sys_command.append(a_path)

        sys_ret = subprocess.run(sys_command, stdout=subprocess.PIPE)
        sys_ret_json = json.loads(sys_ret.stdout.decode('utf-8'))

        if not sys_ret_json:
            return None

        probe = cls._make_probe_info(sys_ret_json)
        return probe
