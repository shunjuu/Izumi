import sys
import os

import shutil
import tempfile

import pprint as pp

# The upload command that is used to upload files.
UPLOAD = "rclone copy %s %s %s"

class OSHandler:
    """
    OSHandler takes care of moving around files, creating and deleting files and temp.
    directories, and calling rclone to upload the files.
    """

    def __init__(self, conf, args, fileh):
        """
        Args:
            conf - a ConfigHandler that should already be populated
            args - an ArgumentHandler that should already be populated
            fileh - a FileHandler that should already be populated
        """

        self._conf = conf
        self._args = args
        self._fileh = fileh

        self.temp_dir = None # This stores the path of the temporary directory

    def _create_temp_dir(self):
        """
        Creates a temporary directory and sets the class variable to it.
        """
        try:
            self.temp_dir = tempfile.mkdtemp(dir=sys.path[0])
            if not self.temp_dir.endswith("/"):
                self.temp_dir += "/"
        except:
            # TODO: print error messages
            sys.exit(2)

    def create_temp_replica_fs(self):
        """
        This method creates the temporary replica of how the new episode
        would be uploaded, under the temp folder. For example:

        temp/"Airing"/"$SHOW"/"$EPISODE"
        """

        # We need to first create the temporary directory to store everything in
        self._create_temp_dir()

        airing = self._conf.get_airing_folder_name()
        show = self._fileh.get_show()
        episode = self._fileh.get_episode_new()

        path = self.temp_dir + airing + show + "/" 

        # Make the path which rclone will be copying to
        os.makedirs(path)

        # Hard link the original file to the new episode name
        source_file = self.__get_source_file()
        new_episode_path = os.path.abspath(path + episode)
        os.link(source_file, new_episode_path)

        # We want to hardlink here because it's instant and 
        # doesn't tax our FS


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

        return os.path.abspath(episode_path)

    def upload(self):
        """
        Uploads the existing files into the various rclone upload destinations.

        Because we've generated an example FS, we'll simply copy the root
        of that folder online as is.
        """
        for dest in self._conf.get_destinations():
            os.system(UPLOAD % (self.temp_dir, dest, self._conf.get_rclone_flags()))

    def cleanup(self):
        """
        Removes the temporary directory files, as well as the source file
        that triggered this entire application.
        """
        self._delete_temp_all()
        self._delete_src_object()

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
            except:
                # TODO: print error messages
                sys.exit(2)

        # It wasn't a directory created
        else:
            # If the episode was provided without a show, the watch folders will match.
            conf_watch_folder = os.path.abspath(self._conf.get_watch_folder())
            args_watch_folder = os.path.abspath(args[0])

            if args_watch_folder == conf_watch_folder:
                os.remove(os.path.abspath(args[0] + args[2]))

            # If we reached this else point, it means a folder/show name
            # was provded at the start, which means it will be args[0]
            else:
                shutil.rmtree(os.path.abspath(args[0]))


    def _delete_temp_all(self):
        """
        Deletes the temporary directory and all of its children data.
        In other words, delete all traces of temp whatsoever.
        """
        try:
            shutil.rmtree(self.temp_dir)
        except:
            # TODO: print error messages
            sys.exit(2)


    def get_temp_dir(self):
        """
        Gets the path of the temporary directory
        """
        return self.temp_dir