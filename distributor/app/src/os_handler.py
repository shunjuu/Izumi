import os
import sys

import shutil
import tempfile
import json

import pprint as pp 

from src.prints.os_handler_prints import OSHandlerPrints

RCLONE_SOURCE = '/rclone/rclone --config=\"/conf/rclone.conf\" '
# The upload command to pull files
DOWNLOAD = RCLONE_SOURCE + "copyto \"{}\" \"{}\" {}"
# The upload command that is used to upload files
UPLOAD = RCLONE_SOURCE + "copy \"{}\" \"{}\" {}"
# The first two are source and dest, the third is the user-specified flags
LIST = RCLONE_SOURCE + 'lsjson -R \"{}{}\" 2>/dev/null'
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
            self._temp_src_dir = tempfile.mkdtemp(dir="/src")
            # Append a "/" if it's not already there
            if not self._temp_src_dir.endswith("/"):
                self._temp_src_dir += "/"

            self._logger.info(self._prints.TEMP_DIR_CREATE_SUCCESS.format(self._temp_src_dir))

        except Exception as e:
            self._logger.error(self._prints.TEMP_DIR_CREATE_ERROR)
            os._exit(2)


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
            episode_list = os.popen(LIST.format(source, self._reqh.get_show())).read()
            episode_list = json.loads(episode_list)

            # If one of the episodes is the episode we want, return True
            for episode in episode_list:
                if episode['Name'] == self._reqh.get_episode():
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
        source_file = source + self._reqh.get_show() + "/" + self._reqh.get_episode()

        # Because of ffmpeg limitations, the file needs to be downloaded first
        # as "temp.mkv" and have no : or special chars in the path
        dest_file = self._temp_src_dir + self._reqh.get_show() + "/" + \
            self._reqh.get_episode()

        self._logger.warning(self._prints.DOWNLOAD_START.format(
            self._reqh.get_episode(), source))
        #print(DOWNLOAD.format(source_file, dest_file, self._conf.get_download_rclone_flags()))
        os.system(DOWNLOAD.format(source_file, dest_file, self._conf.get_download_rclone_flags()))

        self._logger.warning(self._prints.DOWNLOAD_COMPLETE.format(
            self._reqh.get_episode(), source))

        return dest_file


    def download(self):
        """
        Downloads the new episode from the first source possible.

        Returns: True if the download succeeded, false if it failed.
        """

        # First step: Find which rclone source has the file

        if self._reqh.get_sub_type() == "softsub":
            sources = self._conf.get_download_rclone_softsub()
        elif self._reqh.get_sub_type() == "hardsub":
            sources = self._conf.get_download_rclone_hardsub()
        else:
            self._logger.error(self._prints.REQH_FAILURE.format(self._reqh.get_sub_type()))
            sys.exit(3)

        for source in sources:
            if self._check_if_episode_exists(source):
                # TODO: Print some stuff
                self._logger.warning(self._prints.EPISODE_FOUND.format(
                    self._reqh.get_episode(), source))
                self._create_temp_dir()
                self._temp_src_file = self._download_episode(source)
                return True
            else:
                # TODO: Print some stuff
                continue

        # If we've reached this point, the episode was not found
        self._logger.error(self._prints.EPISODE_NOT_FOUND.format(
            self._reqh.get_episode()))
        sys.exit(5)
  
    def upload(self):
        """
        Upload the newly generated file into the rclone destinations.
        Because the replica FS already has been created, just copy the temp
        path. 

        Be sure to remove the src file, if it still exists (which it should).

        Returns the name of the new (EXT) file, no path
        """

        # Remove the src file
        if self._reqh.get_sub_type() == "softsub":
            dests = self._conf.get_upload_rclone_softsub()
        elif self._reqh.get_sub_type() == "hardsub":
            dests = self._conf.get_upload_rclone_hardsub()
        else:
            self._logger.error(self._prints.REQH_FAILURE.format(self._reqh.get_sub_type()))
            sys.exit(3)

        for dest in dests:
            self._logger.warning(self._prints.UPLOAD_START.format(dest))
            #print(UPLOAD.format(self._temp_src_dir, dest, self._conf.get_upload_rclone_flags()))
            os.system(UPLOAD.format(self._temp_src_dir, dest, self._conf.get_upload_rclone_flags()))
            self._logger.warning(self._prints.UPLOAD_COMPLETE.format(dest))

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
            os._exit(2)


    def cleanup(self):
        """
        Purge the temporary folder and anything in it
        """

        # Delete the temp folder and everything in it 
        self._delete_temp_all()
