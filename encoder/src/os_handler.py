import os
import sys

import shutil
import tempfile
import json

import pprint as pp 

# The upload command to pull files
DOWNLOAD = "rclone copyto \"{}\" \"{}\" {}"
# The first two are source and dest, the third is the user-specified flags
LIST = 'rclone lsjson -R \"{}{}\" 2>/dev/null'

class OSHandler:
    """
    Handles downloading, encoding, and uploading files. Uses rclone in system bin for now.
    """

    def __init__(self, conf, reqh):
        """
        Args:
            conf - a ConfigHandler that should already be populated
            reqh - a RequestHandler that should already be populated
        """

        self._conf = conf 
        self._reqh = reqh

        self._temp_dir = None # Store the temporary directory we're working in
        self._temp_src_file = None # Where the temporary src file downloaded is

    
    def _create_temp_dir(self):
        """
        Creates a temporary directory and sets the class variable to it.
        """
        try:
            # tempfile.mkdtemp returns the absolute path
            self.temp_dir = tempfile.mkdtemp(dir=sys.path[0])
            # Append a "/" if it's not already there
            if not self.temp_dir.endswith("/"):
                self.temp_dir += "/"

            #self._logger.info(self._prints.TEMP_DIR_CREATE_SUCCESS.format(self.temp_dir))
        except Exception as e:
            # TODO: print error messages
            #self._logger.error(self._prints.TEMP_DIR_CREATE_ERROR)
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
            rsource = source + self._conf.get_download_softsub_folder()
            episode_list = os.popen(LIST.format(rsource, self._reqh.get_show())).read()
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
        source_file = source + self._conf.get_download_softsub_folder() + \
            self._reqh.get_show() + "/" + self._reqh.get_episode()

        # Because of ffmpeg limitations, the file needs to be downloaded first
        # as "temp.mkv" and have no : or special chars in the path
        dest_file = self.temp_dir + "temp.mkv"

        print(DOWNLOAD.format(source_file, dest_file, self._conf.get_download_rclone_flags()))
        #os.system(DOWNLOAD.format(source_file, dest_file, self._conf.get_download_rclone_flags()))

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
                self._create_temp_dir()
                self._temp_src_file = self._download_episode(source)
            else:
                # TODO: Print some stuff
                continue