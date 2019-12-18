"""
Handles FFMPEG tasks

Commands mostly start with [binary, -i, srcfile]
Alternatively, they could be [binary, -hide_banner, -loglevel, panic, -i, srcfile]
"""

import shutil
import subprocess
import time

from typing import Tuple

from src.shared.constants.Job import Job #pylint: disable=import-error
from src.shared.modules.haikan import Haikan #pylint: disable=import-error

from src.shared.factory.utils.BinUtils import BinUtils #pylint: disable=import-error
from src.shared.factory.utils.DockerUtils import DockerUtils #pylint: disable=import-error
from src.shared.factory.utils.LoggingUtils import LoggingUtils #pylint: disable=import-error
from src.shared.factory.utils.PathUtils import PathUtils #pylint: disable=import-error

from src.encoder.factory.utils.AssetUtils import AssetUtils #pylint: disable=import-error
from src.encoder.exceptions.errors.FFmpegError import FFmpegError #pylint: disable=import-error

class FFmpeg:

    @staticmethod
    def prepare(job: Job, src_file: str, tempfolder: str) -> Tuple[bool, str, str]:
        """
        Takes the temporary file downloaded and copies over streams that we need.
        Does NOT do any encoding or format conversion, just copies to set metadata and remove attachments.

        Important: This will replace the original temp file

        job: The job to handle
        src_file: The downloaded source file (temp.mkv in a tempfolder)
        tempfolder: The tempfolder path itself

        Returns the success of the operation
        """

        info = Haikan.scan(src_file) # Get the information of the source file
        binary = FFmpeg._binary(info) # This is the ffmpeg/ffmpeg-10bit executable path

        # Extract the main sub file if it exists - simplifies future encoding
        sub1_file = PathUtils.clean_directory_path(tempfolder) + "sub1.ass"
        LoggingUtils.debug("Extracting main subtitle file to {}".format(sub1_file))
        command = [binary, "-i", src_file] # ffmpeg -i temp.mkv
        command.extend(["-map", "0:{}".format(info.subtitle_main_index), sub1_file]) # -map 0:2 sub1.ass
        result = subprocess.run(command, stderr=subprocess.PIPE)
        if result.returncode !=0:
            raise FFmpegError("Error occured while extracting the main subtitle file", result.stderr.decode('utf-8'))
        LoggingUtils.debug("Successfully extracted main subtitle file", color=LoggingUtils.GREEN)

        # Extract the secondary sub file if it exists - simplifies future encoding
        sub2_file = None
        if info.subtitle_extra_index != -1:
            sub2_file = PathUtils.clean_directory_path(tempfolder) + "sub2.ass"
            LoggingUtils.debug("Extracting secondary subtitle file to {}".format(sub2_file))
            command = [binary, "-i", src_file] # ffmpeg -i temp.mkv
            command.extend(["-map", "0:{}".format(info.subtitle_extra_index), sub2_file])
            result = subprocess.run(command, stderr=subprocess.PIPE)
            if result.returncode != 0:
                LoggingUtils.warning("Error occured while extracting secondary subtitle file, ignoring", color=LoggingUtils.YELLOW)
                sub2_file = None
            else:
                LoggingUtils.debug("Sucessfully extracted secondary subtitle file", color=LoggingUtils.GREEN)

        dest_temp_file = PathUtils.clean_directory_path(tempfolder) + "temp2.mkv" # Where the new file will be temporarily stored
        LoggingUtils.debug("Creating new prepared file at {}".format(dest_temp_file))
        command = [binary, "-i", src_file] # The base command, this is akin to "ffmpeg -i temp.mkv"
        command.extend(["-map", "0:{}".format(info.video_stream_index)]) # Add the video map stream
        command.extend(["-map", "0:{}".format(info.audio_stream_index)]) # Add the audio map stream
        command.extend(["-c:a", "copy", "-c:v", "copy", dest_temp_file])

        # Create the new file
        LoggingUtils.debug("Running command {}".format(' '.join(command)))
        result = subprocess.run(command, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise FFmpegError("Error occured while ffmpeg was preparing the episode", result.stderr.decode('utf-8'))

        # Replace the original file with this
        LoggingUtils.debug("Successfully prepared the episode, now replacing original...", color=LoggingUtils.GREEN)
        shutil.move(dest_temp_file, src_file)
        LoggingUtils.debug("Successfully replaced original file with prepared episode", color=LoggingUtils.GREEN)

        # We have to run another clear copy - this removes any corrupted tracks, usually subtitles
        command = [binary, "-i", src_file, "-c", "copy", dest_temp_file]
        subprocess.run(command, stderr=subprocess.PIPE)
        shutil.move(dest_temp_file, src_file)

        return sub1_file, sub2_file

    @staticmethod
    def add_font(job: Job, src_file: str, tempfolder: str) -> bool:
        """Adds the OpenSans-Semibold.ttf font file"""
        info = Haikan.scan(src_file)
        binary = FFmpeg._binary(info)
        dest_temp_file = PathUtils.clean_directory_path(tempfolder) + "temp2.mkv"
        LoggingUtils.debug("Creating new fonted file at {}".format(dest_temp_file))

        command = [binary, "-i", src_file] # The base command, this is akin to "ffmpeg -i temp.mkv"
        command.extend(["-attach", AssetUtils.opensans_semibold]) # The attach command, "-attach OpenSans-Semibold.ttf"
        command.extend(["-metadata:s:{}".format(info.streams), "mimetype=application/x-truetype-font"]) # Add metadata
        command.extend(["-c:a", "copy", "-c:v", "copy", "-c:s", "copy", dest_temp_file])

        LoggingUtils.debug("Running command {}".format(' '.join(command)))
        result = subprocess.run(command, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise FFmpegError("Error occured while ffmpeg was attaching font to the episode", result.stderr.decode('utf-8'))

        # Replace the original file with this
        LoggingUtils.debug("Successfully added font to file, now replacing original...", color=LoggingUtils.GREEN)
        shutil.move(dest_temp_file, src_file)
        LoggingUtils.debug("Successfully replaced original file with fonted episode", color=LoggingUtils.GREEN)

    @staticmethod
    def hardsub(job: Job, src_file: str, tempfolder: str, sub1_file: str, sub2_file: str) -> Tuple[bool, str]:
        """Hardsubs the video"""
        info = Haikan.scan(src_file)
        binary = FFmpeg._binary(info)

        # Encode the new hardsub with the main track into a temp.mp4 file
        hardsub_file = PathUtils.clean_directory_path(tempfolder) + "temp.mp4"
        LoggingUtils.debug("Creating new hardsub file at {}".format(hardsub_file))
        command = [binary, "-i", src_file] # The base command, akin fo "ffmpeg -i temp.mkv"
        # If we're in Docker, the ONLY font that will be available should be the Encoder Assets folder
        if DockerUtils.docker:
            LoggingUtils.debug("Detected Docker mode, referencing assets folder for fonts", color=LoggingUtils.YELLOW)
            command.extend(["-vf", "subtitles={sub}:force_style='FontName=Open Sans Semibold:fontsdir={ftd}'".format(
                sub=sub1_file, 
                ftd=PathUtils.clean_directory_path(DockerUtils.path) + "src/encoder/assets/")]) 
        # Otherwise, we have to reference it from PathUTils
        else:
            LoggingUtils.debug("Detected interactive mode, referencing assets folder for fonts", color=LoggingUtils.YELLOW)
            command.extend(["-vf", "subtitles={sub}:force_style='FontName=Open Sans Semibold:fontsdir={ftd}'".format(
                sub=sub1_file, 
                ftd=PathUtils.clean_directory_path(PathUtils.abspath_root()) + "src/encoder/assets/")]) 
        #command.extend(["-ss", "00:03:00", "-t", "00:00:15"]) # Dev mode stuff

        # Sometimes, the audio provided is not HTML5 friendly. If the audio track is not FLAC/MP3/AAC, re-encode it:
        audio_codec = info.audio_codec_name.lower()
        if not (audio_codec == "aac" or audio_codec == "mp3" or audio_codec == "flac"):
            LoggingUtils.debug("Detected audio codec is not HTML5 supported, changing to AAC.")
            command.extend(["-acodec", "aac", "-ab", "320k"])
        else:
            LoggingUtils.debug("Detected audio codec is HTML5-supported codec {}, not changing".format(audio_codec))
            command.extend(["-c:a", "copy"])

        # Some extra flags we use for encoding
        command.extend(["-strict", "-2", "-y", hardsub_file])

        LoggingUtils.debug("Starting hardsub encode of file with main subtitle track...", color=LoggingUtils.YELLOW)
        LoggingUtils.debug("Running command {}".format(' '.join(command)))
        result = subprocess.run(command, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise FFmpegError("Error occured while encoding the file with the main subtitle track", result.stderr.decode('utf-8'))

        LoggingUtils.debug("Successfully encoded hardsub of file with main subtitle track", color=LoggingUtils.GREEN)

        # If there's a secondary track, we want to encode that too
        if sub2_file:
            LoggingUtils.debug("Detected extra subtitle track, now hardsubbing again with extra track")
            extra_file = PathUtils.clean_directory_path(tempfolder) + "temp2.mp4"
            LoggingUtils.debug("Creating secondary hardsub file at {}".format(extra_file))
            command = [binary, "-i", hardsub_file] # ffmpeg -i temp.mp4
            command.extend(["-vf", "subtitles={}:force_style='FontName=Open Sans Semibold'".format(sub2_file)])
            command.extend(["-c:a", "copy", "-strict", "-2", "-y", extra_file])

            LoggingUtils.debug("Starting hardsub encode of file with extra subtitle track...", color=LoggingUtils.YELLOW)
            LoggingUtils.debug("Running command {}".format(' '.join(command)))
            result = subprocess.run(command, stderr=subprocess.PIPE)
            if result.returncode != 0:
                raise FFmpegError("Error occured while encoding the file with extra subtitle track", result.stderr.decode('utf-8'))

            LoggingUtils.debug("Successfully encoded hardsub of file with extra subtitle track", color=LoggingUtils.GREEN)
            shutil.move(extra_file, hardsub_file)
        else:
            LoggingUtils.debug("Didn't detect an extra subtitle track, skipping secondary hardsub run")

        return hardsub_file

    @staticmethod
    def _binary(info: Haikan.ProbeInfo) -> str:
        """Returns which version of ffmpeg to use"""
        if info.video_bits == 8:
            return BinUtils.ffmpeg
        elif info.video_bits == 10:
            return BinUtils.ffmpeg10
