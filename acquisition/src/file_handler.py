import sys
import os

import pprint as pp

import anitopy

from time import sleep 

from bin import hisha2

class FileHandler:
    """
    FileHandler stores all the properties of the new file (episode), or finds them
    if not provided.

    Because of its nature dealing with Files, FileHandler does make system calls 
    if necessary to find files (in the event of an ISDIR creation)
    """

    def __init__(self, conf, args, inote):
        """
        Args: 
            conf - a ConfigHandler that should already be populated
            args - an ArgumentHandler that should already be populated

            FileHandler will automatically determine properties upon initialization
        """

        # Store the Config and Argument Handler as "private" variables
        self._conf = conf
        self._args = args
        self._inote = inote

        # -------------------
        # Variables
        # -------------------

        self.episode = None # A string representation, the name of the new file with file extension
        self.episode_new = None # String rep of the new filename after Anitopy cleans it up
        self.show = None # A string representation of the show of the new file. No "/" at the end
        self.filesize = None # An integer representation of the size of the file, in bytes
        self.sub_type = None # One of "hardsub" or "softsub", determined by file extension solely

        # -------------------
        # Populate the variables
        # -------------------

        # self.episode NEEDS to be run before self._load_show()
        self.episode = self._load_episode(conf, args)
        self.show = self._load_show(args)
        self.filesize = self._load_filesize(conf, args)
        self.sub_type = self._load_sub_type(self.episode)


    def _load_episode(self, conf, args):
        """
        Gets the episode name from the ArgumentHandler, or finds it if this is an ISDIR event.

        Params:
            conf: A ConfigHandler object that is already populated
            args: An ArgumentHandler object that is already populated

        Returns: The name of the episode as a string (includes extension)
        """

        # If the inote event was not ISDIR, then ArgumentHandler will already have the episode 
        episode = args.get_episode()
        if episode:
            return episode

        # But if this is not an ISDIR event, then we need to find the new episode in the directory
        # We will make sure there's only one file in the diretory, but this is mostly
        # to make sure a hardlink wasn't suddenly inserted

        # An ISDIR event would have been created at the root of the watch directory, since
        # nested directories are not supported. Fetch the watch directory with the show directory
        # and find the files inside it.

        # We will also wait one second for hardlink buffering
        sleep(1)

        episode_folder = conf.get_watch_folder() + args.get_show() + "/"
        episode_folder_contents = os.listdir(episode_folder)
        episode_folder_contents = [f for f in episode_folder_contents if f.endswith('.mkv')]

        if len(episode_folder_contents) != 1:
            ## TODO: We need to print an error message here and end with it.
            sys.exit(1)

        # If there's only one file within the folder, then we know the new episode
        # has to be that specific file (also ending in .mkv)
        episode = episode_folder_contents[0]

        return episode


    def _load_show(self, args):
        """
        Gets the show name from the ArgumentHandler, or finds it if a new episode was downloaded without
        including the name of the show.

        Params:
            conf: A ConfigHandler object that is already populated
            args: An ArgumentHandler object that is already populated

        Returns: The name of the show of the episode as a string
        """

        # Args may already have determined the show from the passed-in args. If so, just return that.
        show = args.get_show()
        if show:
            return show

        # If the show wasn't included, this means the episode was included on its own.
        # What's nice about this? The Hisha library takes care of it for us.
        show = hisha2.hisha(self.episode)

        return show


    def _load_filesize(self, conf, args):
        """
        Gets the filesize of the new file to be uploaded.

        Params:
            conf: A ConfigHandler object that is already populated
            args: An ArgumentHandler object that is already populated

        Returns: The size of the episode (in bytes)
        """

        # There are a finite amount of ways in which this program was executed.
        # 1. An ISDiR event
        # 2. Episode with show already specified
        # 3. Episode without the show already specified

        # If there is an ISDIR, we need to check the file within the directory
        # Otherwise, we can actually get the size from the system arguments

        # ISDiR event:
        if 'isdir' in sys.argv[1].lower():
            episode_path = conf.get_watch_folder() + args.get_show() + "/" + self.episode
            size = os.path.getsize(episode_path)
            return size

        # In either case where there is no ISDIR event, then the inote will point
        # us directly to the file. It's easier to use it directly instead of 
        # pulling it from the args.
        delimiter = self._conf.get_delimiter()
        args = self._inote.split(delimiter)

        episode_path = args[0] + args[2]
        size = os.path.getsize(episode_path)
        return size


    def _load_sub_type(self, episode):
        """
        Determines whether the new episode file is a:
            - "softsub"
            - "hardsub"

        Params:
            episode - name of the new episode file

        Returns: "hardsub" or "softsub", or None if neither
        """

        if episode.endswith(".mkv"):
            return "hardsub"

        elif episode.endswith('.mp4'):
            return "softsub"

        else: 
            return None

    def _generate_new_episode(self, episode): 
        """
        Takes the old filename and generates a new, clean name for it.

        Params:
            episode - the name of the old episode file

        Return: A "cleaned" filename
        """

        # Parse the filename
        a = anitopy.parse(episode)

        # Generate the new episode name
        new_episode = a['anime_title'] + " - " + a['episode_number']

        # Mark video resolution
        if 'video_resolution' in a:
            new_episode = new_episode + " [" + a['video_resolution'] + "]"

        # Mark if uncensored
        if 'other' in a and 'uncensored' in a['other'].lower():
            new_episode += " (Uncensored)" 

        # Add the extension
        _, ext = os.path.splitext(episode)
        new_episode += ext

        return new_episode


    # --------------------
    # Getters!
    # --------------------

    def get_episode(self):
        """
        Gets the file's episode name as a string
        """
        return self.episode

    def get_show(self):
        """
        Get's the file's show as a string
        """
        return self.show

    def get_filesize(self):
        """
        Get's the file's size in bytes as an integer
        """
        return self.filesize

    def get_sub_type(self):
        """
        Gets the file's sub type as a string
        """
        return self.sub_type