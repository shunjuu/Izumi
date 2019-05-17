import os
import sys

import shutil
import tempfile
import json

import pprint as pp 

from src.prints.os_handler_prints import OSHandlerPrints
from src.encode.h264_standard import H264Standard

RCLONE_SOURCE = ('/bin2/rclone --config=\"/bin2/rclone.conf\" '
                if 'DOCKER' in os.environ and bool(os.environ.get("DOCKER"))
                else "rclone ")
# The upload command to pull files
DOWNLOAD = RCLONE_SOURCE + "copyto \"{}\" \"{}\" {}"
# The upload command that is used to upload files
UPLOAD = RCLONE_SOURCE + "copy \"{}\" \"{}\" {}"
# The first two are source and dest, the third is the user-specified flags
LIST = RCLONE_SOURCE + "lsjson -R \"{}{}\" 2>/dev/null"
# The video extension
EXT = ".mp4"

class OSHandler:
    """
    Handles downloading, encoding, and uploading files. Uses rclone in system bin for now.
    """

    def __init__(self, conf, reqh, printh):
        """
        Args:
            conf - a ConfigHandler that should already be populated
            reqh - a RequestHandler that should already be populated
        """

        self._conf = conf 
        self._reqh = reqh

        # Logging Tools
        self._logger = printh.get_logger()
        self._printh = printh
        self._prints = OSHandlerPrints(printh.Colors())

        self._temp_src_dir = None # Store the temporary directory we're working in
        self._temp_src_file = None # Where the temporary src file downloaded is

        self._temp_out_dir = None # Full dir path of new file. Overlaps with self._temp_src_dir
        self._temp_out_file = None # Where the encoded file is located


    def _create_temp_dir(self):
        """
        Creates a temporary directory and sets the class variable to it.
        """
        try:
            # tempfile.mkdtemp returns the absolute path
            #self._temp_src_dir = tempfile.mkdtemp(dir=sys.path[0])
            self._temp_src_dir = tempfile.mkdtemp(dir=sys.path[0])
            # Append a "/" if it's not already there
            if not self._temp_src_dir.endswith("/"):
                self._temp_src_dir += "/"

            self._logger.info(self._prints.TEMP_DIR_CREATE_SUCCESS.format(self._temp_src_dir))

        except Exception as e:
            self._logger.error(self._prints.TEMP_DIR_CREATE_ERROR)
            raise Exception()


    def _check_if_episode_exists(self, source):
        """
        Checks if an episode exists.

        Params:
            source - the rclone source to pull from

        Returns:
            True if the episode exists, False if not
        """

        # If a softsub folder was mentioned, add it here.
        try:
            rsource = source + self._conf.get_download_softsub_folder()
            episode_list = os.popen(LIST.format(rsource, self._reqh.show)).read()
            episode_list = json.loads(episode_list)

            # If one of the episodes is the episode we want, return True
            for episode in episode_list:
                if episode['Name'] == self._reqh.episode:
                    return True

            # If the path exists but none of them are the episode, return False
            return False

        except:
            # Usually thrown if the destination does not exist.
            return False


    def _download_episode(self, source):
        """
        Helper to actually download the file given from source to local. 

        For the sake of simplicity, the source file will be downloaded
        as "temp.mkv" (also to ensure -vf subtitles compatibility)

        Returns the full path of the temp file (/..../temp.mkv)
        """

        # Get the command for the source file location
        source_file = source + self._conf.get_download_softsub_folder() + \
            self._reqh.show + "/" + self._reqh.episode

        # Because of ffmpeg limitations, the file needs to be downloaded first
        # as "temp.mkv" and have no : or special chars in the path
        dest_file = self._temp_src_dir + "temp.mkv"

        self._logger.warning(self._prints.DOWNLOAD_START.format(
            self._reqh.episode, source))
        #print(DOWNLOAD.format(source_file, dest_file, self._conf.get_download_rclone_flags()))
        os.system(DOWNLOAD.format(source_file, dest_file, self._conf.get_download_rclone_flags()))

        self._logger.warning(self._prints.DOWNLOAD_COMPLETE.format(
            self._reqh.episode, source))

        return dest_file


    def download(self):
        """
        Downloads the new episode from the first source possible.

        Returns: True if the download succeeded, false if it failed.
        """

        # First step: Find which rclone source has the file
        for source in self._conf.get_download_download_sources():
            if self._check_if_episode_exists(source):
                # TODO: Print some stuff
                self._logger.warning(self._prints.EPISODE_FOUND.format(
                    self._reqh.episode, source))
                self._create_temp_dir()
                self._temp_src_file = self._download_episode(source)
                return True
            else:
                # TODO: Print some stuff
                continue

        # If we've reached this point, the episode was not found
        self._logger.error(self._prints.EPISODE_NOT_FOUND.format(
            self._reqh.episode))
        raise Exception()
  

    def _create_temp_replica_fs(self):
        """
        Create the temp replica FS:
        temp/"Airing [Hardsub]"/"$SHOW"
        """
        hardsub_folder = self._conf.get_upload_hardsub_folder()
        show_name = self._reqh.show + "/" # Show doesn't end with "/"
        self._temp_out_dir = self._temp_src_dir + hardsub_folder + show_name

        os.makedirs(self._temp_out_dir)
        self._logger.info(self._prints.TEMP_REPLICA_FS.format(self._temp_out_dir))

        return


    def _create_hardsub_file_name(self):
        """
        Create the full/absolute path for the to-be hardsub file (.mp4)
        /temp/"Airing [Hardsub]"/"$SHOW.mp4"
        """
        # Get the parts of the filename
        filename, ext = os.path.splitext(self._reqh.episode)
        # Generate the same name... as the hardsub type
        hardsub_file = filename + EXT

        self._logger.info(self._prints.HARDSUB_FILE_NAME.format(hardsub_file))
        return hardsub_file


    def encode(self):
        """
        Takes the temp file and encodes it into what we want.

        1. In the same temp directory, replicate the path fs for the new file
           This includes the "Airing [Hardsub]" folder
        2. Generate the path for the new mp4
        3. Pass the source and the out file paths to the encoder
        4. Profit

        Returns the filesize of the new file as an integer in bytes
        """
        self._create_temp_replica_fs()
        self._temp_out_file = self._create_hardsub_file_name()

        encoder = H264Standard(self._conf, self._printh, 
            self._temp_src_file, self._temp_out_dir, self._temp_out_file)
        encoder.encode()

        out_file_size = os.path.getsize(self._temp_out_dir + self._temp_out_file)
        self._logger.info(self._prints.HARDSUB_FILE_SIZE.format(out_file_size))
        return out_file_size


    def upload(self):
        """
        Upload the newly generated file into the rclone destinations.
        Because the replica FS already has been created, just copy the temp
        path. 

        Be sure to remove the src file, if it still exists (which it should).

        Returns the name of the new (EXT) file, no path
        """

        # Remove the src file
        try:
            os.remove(self._temp_src_file)
            self._logger.warning(self._prints.UPLOAD_REMOVE_SRC_FILE.format(
                self._temp_src_file))
        except:
            self._logger.error(self._prints.UPLOAD_REMOVE_SRC_FILE_FAIL.format(
                self._temp_src_file))
            raise Exception()

        for dest in self._conf.get_upload_destinations():
            self._logger.warning(self._prints.UPLOAD_START.format(dest))
            os.system(UPLOAD.format(self._temp_src_dir, dest, self._conf.get_upload_rclone_flags()))
            self._logger.warning(self._prints.UPLOAD_COMPLETE.format(dest))

        # For now, return the new file name
        return self._reqh.episode.replace(".mkv", EXT) 


    # Cleanup methods

    def _delete_temp_all(self):
        """
        Deletes the temporary directory and all of its children data.
        In other words, deletes all traces of temp whatsoever.
        """
        self._logger.warning(self._prints.DELETE_TEMP_FOLDER.format(self._temp_src_dir))
        try:
            shutil.rmtree(self._temp_src_dir)
            self._logger.warning(self._prints.DELETE_TEMP_FOLDER_SUCCESS.format(
                self._temp_src_dir))
        except:
            self._logger.error(self._prints.DELETE_TEMP_FOLDER_FAIL.format(
                self._temp_src_dir))
            # Don't raise an exception or exit - just leave it in the logs


    def cleanup(self):
        """
        Purge the temporary folder and anything in it
        """

        # Delete the temp folder and everything in it 
        self._delete_temp_all()
