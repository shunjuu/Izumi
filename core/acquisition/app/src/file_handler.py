import sys
import os

import pprint as pp

import anitopy

from time import sleep 

from bin import hisha2
from src.prints.file_handler_prints import FileHandlerPrints

class FileHandler:
    """
    FileHandler stores all the properties of the new file (episode), or finds them
    if not provided.

    Because of its nature dealing with Files, FileHandler does make system calls 
    if necessary to find files (in the event of an ISDIR creation)
    """

    def __init__(self, conf, args, printh, inote):
        """
        Args: 
            conf - a ConfigHandler that should already be populated
            args - an ArgumentHandler that should already be populated
            printh - a PrintHandler that should already be populated

            FileHandler will automatically determine properties upon initialization
        """

        # Store the Config and Argument Handler as "private" variables
        self._conf = conf
        self._args = args
        self._inote = inote

        # Logging Tools
        self._logger = printh.logger
        self._prints = FileHandlerPrints(printh.Colors(), self._conf)

        # -------------------
        # Variables
        # -------------------

        self._episode = None # A string representation, the name of the new file with file extension
        self._episode_new = None # String rep of the new filename after Anitopy cleans it up
        self._show = None # A string representation of the show of the new file. No "/" at the end
        self._show_clean = None # self._show, but with : replaced with " - "
        self._filesize = None # An integer representation of the size of the file, in bytes
        self._sub_type = None # One of "hardsub" or "softsub", determined by file extension solely

        # -------------------
        # Populate the variables
        # -------------------

        try:
            # self._episode NEEDS to be run before self._load_show()
            self._episode = self._load_episode(conf, args)
            self._episode_new = self._generate_new_episode(self._episode)
            self._show = self._load_show(args)
            self._show_clean = self._generate_clean_show(self._show)
            self._filesize = self._load_filesize(conf, args)
            self._sub_type = self._load_sub_type(self._episode)
        except Exception as e:
            # Generally in this case, it means an ISDIR event occured, and a filenotfound error
            # was thrown cause the og file was deleted in the previous call.
            self._logger.error(e)
            self._logger.error(self._prints.ISDIR_FILE_NOT_FOUND)
            raise Exception()


    def _load_episode(self, conf, args):
        """
        Gets the episode name from the ArgumentHandler, or finds it if this is an ISDIR event.

        Params:
            conf: A ConfigHandler object that is already populated
            args: An ArgumentHandler object that is already populated

        Returns: The name of the episode as a string (includes extension)
        """

        # If the inote event was not ISDIR, then ArgumentHandler will already have the episode 
        episode = args.episode
        if episode:
            self._logger.info(self._prints.EPISODE_LOADED_ARG.format(episode))
            return episode

        # But if this is an ISDIR event, then we need to find the new episode in the directory
        # We will make sure there's only one file in the diretory, but this is mostly
        # to make sure a hardlink wasn't suddenly inserted

        # An ISDIR event would have been created at the root of the watch directory, since
        # nested directories are not supported. Fetch the watch directory with the show directory
        # and find the files inside it.

        # We will also wait one second for hardlink buffering
        sleep(1)

        episode_folder = conf.watch_folder + args.show + "/"
        episode_folder_contents = os.listdir(episode_folder)
        episode_folder_contents = [f for f in episode_folder_contents if f.endswith('.mkv')]

        if len(episode_folder_contents) != 1:
            ## TODO: We need to print an error message here and end with it.
            self._logger.error(self._prints.EPISODE_LOADED_ERROR)
            raise Exception()

        # If there's only one file within the folder, then we know the new episode
        # has to be that specific file (also ending in .mkv)
        episode = episode_folder_contents[0]
        self._logger.info(self._prints.EPISODE_LOADED_FOUND.format(episode))

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
        show = args.show
        if show:
            self._logger.info(self._prints.SHOW_LOADED_ARG.format(show))
            return show

        # If the show wasn't included, this means the episode was included on its own.
        # What's nice about this? The Hisha library takes care of it for us.
        show = hisha2.hisha(self._episode)
        self._logger.info(self._prints.SHOW_LOADED_HISHA.format(show))

        # There should be a case where Hisha doesn't find it
        # But hisha3 will need to be developed first

        return show


    def _load_filesize(self, conf, args):
        """
        Gets the filesize of the new file to be uploaded.

        Params:
            conf: A ConfigHandler object that is already populated
            args: An ArgumentHandler object that is already populated

        Returns: The size of the episode (in bytes), as an int
        """

        # There are a finite amount of ways in which this program was executed.
        # 1. An ISDiR event
        # 2. Episode with show already specified
        # 3. Episode without the show already specified

        # If there is an ISDIR, we need to check the file within the directory
        # Otherwise, we can actually get the size from the system arguments

        # ISDiR event:
        if 'isdir' in sys.argv[1].lower():
            episode_path = conf.watch_folder + args.show + "/" + self._episode
            size = os.path.getsize(episode_path)
            self._logger.info(self._prints.FILESIZE_DISPLAY.format(size))
            return size

        # In either case where there is no ISDIR event, then the inote will point
        # us directly to the file. It's easier to use it directly instead of 
        # pulling it from the args.
        delimiter = self._conf.delimiter
        args = self._inote.split(delimiter)

        episode_path = args[0] + args[2]
        size = os.path.getsize(episode_path)
        self._logger.info(self._prints.FILESIZE_DISPLAY.format(size))
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
            self._logger.info(self._prints.SUB_TYPE.format("Softsub"))
            return "softsub"

        elif episode.endswith('.mp4'):
            self._logger.info(self._prints.SUB_TYPE.format("Hardsub"))
            return "hardsub"

        else: 
            self._logger.info(self._prints.SUB_TYPE.format("None"))
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
        new_episode = a['anime_title']

        if 'anime_season' in a:
            new_episode = new_episode + " S" + str(a['anime_season'])

        new_episode = new_episode + " - " + a['episode_number']

        # Mark video resolution
        if 'video_resolution' in a:
            new_episode = new_episode + " [" + a['video_resolution'] + "]"

        # Mark if uncensored
        if 'other' in a and 'uncensored' in a['other'].lower():
            new_episode += " (Uncensored)" 

        # Add the extension
        _, ext = os.path.splitext(episode)
        new_episode += ext

        self._logger.warning(self._prints.EPISODE_NEW_NAME.format(new_episode))
        return new_episode

    def _generate_clean_show(self, show):
        """
        Cleans the show names into file friendly names

        Params:
            show - the name of the old show

        Return: A "cleaned" show name

        Note: This works because Anilist requests do not consider punctuation
        """

        # 1. Get rid of colons and replace with hypen
        clean_show = show.replace(": ", " - ")

        # 2. Get rid of "?"
        clean_show = clean_show.replace("?", "")

        self._logger.warning(self._prints.SHOW_NEW_NAME.format(clean_show))
        return clean_show

    # --------------------
    # Getters!
    # --------------------

    @property
    def episode(self):
        """Gets the file's episode name as a string"""
        return self._episode

    @property
    def episode_new(self):
        """Gets the file's cleaned name as a string"""
        return self._episode_new

    @property
    def show(self):
        """Get's the file's show as a string"""
        return self._show
    
    @property
    def show_clean(self):
        """Get's the file's show name, but cleaned up"""
        return self._show_clean
    
    @property
    def filesize(self):
        """Get's the file's size in bytes as an integer"""
        return self._filesize

    @property
    def sub_type(self):
        """Gets the file's sub type as a string"""
        return self._sub_type
    