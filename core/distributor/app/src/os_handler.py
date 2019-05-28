import os
import sys

import shutil
import tempfile
import json

import pprint as pp 

from bin import akari # for MAL filtering
from bin import kishi # for Anilist filtering

from src.prints.os_handler_prints import OSHandlerPrints

RCLONE_SOURCE = ('/bin2/rclone --config=\"/bin2/rclone.conf\" '
                if 'DOCKER' in os.environ and bool(os.environ.get("DOCKER"))
                else "rclone ")
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

        # Filtering tools
        self._akari = akari.Akari()
        self._kishi = kishi.Kishi()

        # Logging Tools
        self._logger = printh.logger
        self._printh = printh
        self._prints = OSHandlerPrints(printh.Colors())

        self._temp_src_dir = None # Store the temporary directory we're working in
        self._temp_src_file = None # Where the temporary src file downloaded is

        self._temp_out_dir = None # Full dir path of new file. Overlaps with self._temp_src_dir
        self._temp_out_file = None # Where the encoded file is located


    def _check_filters(self, show):
        """
        Use Akari and Kishi to check if a given user's profile is watching this show.
        Used to filter whether or not notifications should be sent.
        If either profile returns True, return True
        Params:
            show - the name of the show in the request
        Returns: a boolean indicating whether or not the show is being watched
        """

        ani_user = self._conf.distributor_filter_anilist
        mal_user = self._conf.distributor_filter_mal

        # If neither are being used, then return true by default
        if not ani_user and not mal_user:
            self._logger.info(self._prints.FILTER_NOT_USED)
            return True

        # Check both by ID and Names
        if ani_user:
            if self._kishi.is_user_watching_id(ani_user, self._info.id): 
                self._logger.info(self._prints.FILTER_FOUND.format(show, "Anilist", ani_user, "id"))
                return True
            if self._kishi.is_user_watching_names(ani_user, show): 
                self._logger.info(self._prints.FILTER_FOUND.format(show, "Anilist", ani_user, "name"))
                return True

        if mal_user:
            if self._akari.is_user_watching_id(mal_user, self._info.idMal): 
                self._logger.info(self._prints.FILTER_FOUND.format(show, "MyAnimeList", mal_user, "id"))
                return True
            if self._akari.is_user_watching_names(mal_user, show): 
                self._logger.info(self._prints.FILTER_FOUND.format(show, "MyAnimeList", mal_user, "name"))
                return True

        # All checks failed, so return False
        self._logger.info(self._prints.FILTER_SHOW_NOT_FOUND.format(show))
        return False

    def _create_temp_dir(self):
        """
        Creates a temporary directory and sets the class variable to it.
        """
        try:
            # tempfile.mkdtemp returns the absolute path
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
            episode_list = os.popen(LIST.format(source, self._reqh.show)).read()
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
        source_file = source + self._reqh.show + "/" + self._reqh.episode

        # Because of ffmpeg limitations, the file needs to be downloaded first
        # as "temp.mkv" and have no : or special chars in the path
        dest_file = self._temp_src_dir + self._reqh.show + "/" + \
            self._reqh.episode

        self._logger.warning(self._prints.DOWNLOAD_START.format(
            self._reqh.episode, source))
        os.system(DOWNLOAD.format(source_file, dest_file, self._conf.download_rclone_flags))

        self._logger.warning(self._prints.DOWNLOAD_COMPLETE.format(
            self._reqh.episode, source))

        return dest_file


    def download(self):
        """
        Downloads the new episode from the first source possible.

        Returns: True if the download succeeded, false if it failed.
        """

        # First step: Find which rclone source has the file

        if self._reqh.sub_type == "softsub":
            sources = self._conf.download_rclone_softsub
        elif self._reqh.sub_type == "hardsub":
            sources = self._conf.download_rclone_hardsub
        else:
            self._logger.error(self._prints.REQH_FAILURE.format(self._reqh.sub_type))
            raise Exception()

        for source in sources:
            if self._check_if_episode_exists(source):
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
  
    def upload(self):
        """
        Upload the newly generated file into the rclone destinations.
        Because the replica FS already has been created, just copy the temp
        path. 

        Be sure to remove the src file, if it still exists (which it should).

        Returns the name of the new (EXT) file, no path
        """

        # Remove the src file
        if self._reqh.sub_type == "softsub":
            dests = self._conf.upload_rclone_softsub
        elif self._reqh.sub_type == "hardsub":
            dests = self._conf.upload_rclone_hardsub
        else:
            self._logger.error(self._prints.REQH_FAILURE.format(self._reqh.sub_type))
            raise Exception()

        for dest in dests:
            self._logger.warning(self._prints.UPLOAD_START.format(dest))
            os.system(UPLOAD.format(self._temp_src_dir, dest, self._conf.upload_rclone_flags))
            self._logger.warning(self._prints.UPLOAD_COMPLETE.format(dest))


    def distribute(self):
        """
        This is a wrapper method that calls both upload and distribute, but also checks filters
        first.
        """
        if self._check_filters(self._reqh.show):
            self.download()
            self.upload()


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
            # Do not raise an exception here - Just leave it in logs


    def cleanup(self):
        """
        Purge the temporary folder and anything in it
        """

        # Delete the temp folder and everything in it 
        self._delete_temp_all()
