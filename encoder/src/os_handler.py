import os
import sys

import shutil
import tempfile
import json

import pprint as pp 

from src.encode.h264_standard import H264Standard

# The upload command to pull files
DOWNLOAD = "rclone copyto \"{}\" \"{}\" {}"
# The upload command that is used to upload files
UPLOAD = "rclone copy {} {} {}"
# The first two are source and dest, the third is the user-specified flags
LIST = 'rclone lsjson -R \"{}{}\" 2>/dev/null'
# The video extension
EXT = ".mp4"

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
            self._temp_src_dir = tempfile.mkdtemp(dir=sys.path[0])
            # Append a "/" if it's not already there
            if not self._temp_src_dir.endswith("/"):
                self._temp_src_dir += "/"

            #self._logger.info(self._prints.TEMP_DIR_CREATE_SUCCESS.format(self._temp_src_dir))
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
        dest_file = self._temp_src_dir + "temp.mkv"

        #print(DOWNLOAD.format(source_file, dest_file, self._conf.get_download_rclone_flags()))
        os.system(DOWNLOAD.format(source_file, dest_file, self._conf.get_download_rclone_flags()))

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
                return True
            else:
                # TODO: Print some stuff
                continue
  

    def _create_temp_replica_fs(self):
        """
        Create the temp replica FS:
        temp/"Airing [Hardsub]"/"$SHOW"
        """
        hardsub_folder = self._conf.get_upload_hardsub_folder()
        show_name = self._reqh.get_show() + "/" # Show doesn't end with "/"
        self._temp_out_dir = self._temp_src_dir + hardsub_folder + show_name

        os.makedirs(self._temp_out_dir)


    def _create_hardsub_file_path(self):
        """
        Create the full/absolute path for the to-be hardsub file (.mp4)
        /temp/"Airing [Hardsub]"/"$SHOW.mp4"
        """
        # Get the parts of the filename
        filename, ext = os.path.splitext(self._reqh.get_episode())
        # Generate the same name... as the hardsub type
        hardsub_file = filename + EXT

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
        self._temp_out_file = self._create_hardsub_file_path()

        encoder = H264Standard(self._conf, 
            self._temp_src_file, self._temp_out_dir, self._temp_out_file)
        encoder.encode()

        out_file_size = os.path.getsize(self._temp_out_dir + self._temp_out_file)
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
        print(self._temp_src_file)
        try:
            os.remove(self._temp_src_file)
        except:
            pass

        for dest in self._conf.get_upload_destinations():
            os.system(UPLOAD.format(self._temp_src_dir, dest, self._conf.get_upload_rclone_flags()))

        # For now, return the new file name
        return self._reqh.get_episode().replace(".mkv", EXT) 


    # Cleanup methods

    def _delete_temp_all(self):
        """
        Deletes the temporary directory and all of its children data.
        In other words, deletes all traces of temp whatsoever.
        """
        try:
            shutil.rmtree(self._temp_src_dir)
        except:
            os._exit(2)


    def cleanup(self):
        """
        Purge the temporary folder and anything in it
        """

        # Delete the temp folder and everything in it 
        self._delete_temp_all()