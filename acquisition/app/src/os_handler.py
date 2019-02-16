import sys
import os

import shutil
import tempfile

import pprint as pp

from src.prints.os_handler_prints import OSHandlerPrints

# The upload command that is used to upload files.
UPLOAD = "/rclone/rclone --config=\"/conf/rclone.conf\" copy -L \"{}\" \"{}\" {}"

class OSHandler:
    """
    OSHandler takes care of moving around files, creating and deleting files and temp.
    directories, and calling rclone to upload the files.
    """

    def __init__(self, conf, args, fileh, printh):
        """
        Args:
            conf - a ConfigHandler that should already be populated
            args - an ArgumentHandler that should already be populated
            fileh - a FileHandler that should already be populated
            printh - a PrintHandler that should already be populated
        """

        self._conf = conf
        self._args = args
        self._fileh = fileh

        self.temp_dir = None # This stores the path of the temporary directory

        # Logging Tools
        self._logger = printh.get_logger()
        self._prints = OSHandlerPrints(printh.Colors())


    def _create_temp_dir(self):
        """
        Creates a temporary directory and sets the class variable to it.
        """
        try:
            self.temp_dir = tempfile.mkdtemp(dir="/src")
            if not self.temp_dir.endswith("/"):
                self.temp_dir += "/"

            self._logger.info(self._prints.TEMP_DIR_CREATE_SUCCESS.format(self.temp_dir))
        except Exception as e:
            # TODO: print error messages
            self._logger.error(self._prints.TEMP_DIR_CREATE_ERROR)
            os._exit(2)

    def create_temp_replica_fs(self):
        """
        This method creates the temporary replica of how the new episode
        would be uploaded, under the temp folder. For example:

        temp/"Airing"/"$SHOW"/"$EPISODE"

        For FS replacement also replaces ":" with " - "
        """

        # We need to first create the temporary directory to store everything in
        self._create_temp_dir()

        airing = self._conf.get_airing_folder_name()
        show = self._fileh.get_show_clean()
        episode = self._fileh.get_episode_new()

        path = self.temp_dir + airing + show + "/" 

        # Make the path which rclone will be copying to
        os.makedirs(path)
        self._logger.info(self._prints.FS_PATH_CREATION.format(path))

        # Hard link the original file to the new episode name
        source_file = self.__get_source_file()
        new_episode_path = os.path.abspath(path + episode)

        # Output
        self._logger.info(self._prints.FS_PATH_LINK_1.format(source_file))
        self._logger.info(self._prints.FS_PATH_LINK_2.format(new_episode_path))

        try:
            # We want to hardlink here because it's instant and 
            # doesn't tax our FS, but for Docker it may not be possible
            os.link(source_file, new_episode_path)
        except:
            # For cases in Docker where -v is a separate filesystem, 
            # we have no choice but to copy it.
            shutil.move(source_file, new_episode_path)



    def __get_source_file(self):
        """
        Second-level helper that determines the full path of the original file

        Used to create the replica FS and also to delete the original file
        """
        args = sys.argv[1].split(self._conf.get_delimiter())

        if 'isdir' in sys.argv[1].lower():
            episode_path = args[0] + args[2] + "/" + self._fileh.get_episode()
        else:
            episode_path = args[0] + args[2]

        # Get the absolute path
        episode_path = os.path.abspath(episode_path)

        self._logger.info(self._prints.SOURCE_FILE_FOUND.format(episode_path))

        return episode_path

    def upload(self):
        """
        Uploads the existing files into the various rclone upload destinations.

        Because we've generated an example FS, we'll simply copy the root
        of that folder online as is.
        """
        for dest in self._conf.get_destinations():
            self._logger.info(self._prints.RCLONE_UPLOAD_START.format(dest))
            os.system(UPLOAD.format(self.temp_dir, dest, self._conf.get_rclone_flags()))
            self._logger.info(self._prints.RCLONE_UPLOAD_END.format(dest))

    def cleanup(self):
        """
        Removes the temporary directory files, as well as the source file
        that triggered this entire application.
        """
        self._delete_temp_all()

        # Bcause shutil.move may be used instead of link, there is a chance
        # the source file might not exist - because it's been moved
        try:
            self._delete_src_object()
        except:
            pass

    def _delete_src_object(self):
        """
        Deletes the episode (and folder if applicable) that was the
        original file provided to the system.
        """

        args = sys.argv[1].split(self._conf.get_delimiter())

        # If the created object was an ISDIR, then purge the isdir directory
        if 'isdir' in sys.argv[1].lower():
            # Keep folder outside of the try block in case exception occurs
            src_folder = os.path.abspath(args[0] + args[2])
            try:
                shutil.rmtree(src_folder)
                self._logger.warning(self._prints.CLEANUP_SRC_OBJ_ISDIR.format(src_folder))
            except:
                self._logger.error(self._prints.CLEANUP_SRC_OBJ_ISDIR_ERROR.format(src_folder))
                os._exit(2)

        # It wasn't a directory created
        else:
            # If the episode was provided without a show, the watch folders will match.
            conf_watch_folder = os.path.abspath(self._conf.get_watch_folder())
            args_watch_folder = os.path.abspath(args[0])

            if args_watch_folder == conf_watch_folder:
                src_file_path = os.path.abspath(args[0] + args[2])
                os.remove(src_file_path)
                self._logger.warning(self._prints.CLEANUP_SRC_OBJ_FILE_ONLY.format(src_file_path))

            # If we reached this else point, it means a folder/show name
            # was provded at the start, which means it will be args[0]
            else:
                src_folder_path = os.path.abspath(args[0])
                shutil.rmtree(src_folder_path)
                self._logger.warning(self._prints.CLEANUP_SRC_OBJ_FOLDER_PROVIDED.format(src_folder_path))


    def _delete_temp_all(self):
        """
        Deletes the temporary directory and all of its children data.
        In other words, delete all traces of temp whatsoever.
        """
        try:
            shutil.rmtree(self.temp_dir)
            self._logger.warning(self._prints.CLEANUP_TEMP_ALL.format(self.get_temp_dir()))
        except:
            self._logger.error(self._prints.CLEANUP_TEMP_ALL_ERROR.format(self.get_temp_dir()))
            os._exit(2)


    def get_temp_dir(self):
        """
        Gets the path of the temporary directory
        """
        return self.temp_dir