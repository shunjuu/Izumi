import sys
import os

import pprint as pp

class ArgumentHandler:
    """
    Not to be confused with ArgParser, this class is designed to handle
    extracting information from inotify-style strings.

    This class doesn't get any information from online, it just extracts 
    what it can from the argument.
    """

    def __init__(self, conf):
        """
        Args:
            conf: a ConfigHandler which already has the config.yml/json loaded.
        """

        self._conf = conf

        """
        Class variables
        """
        self._inote = None # The current _inote to process

        # Either of these could be none because ISDIR isn't guaranteed to happen
        self.show = None # The show name if provided, else None
        self.episode = None # The name of the episode if provided, else None


    def load_inote(self, inote):
        """
        Loads a new inote into the class. It then automatically 
        sets the self.show and self.episode variables appropriately.

        Params:
            inote: An inote string that this application was executed with.
        """
        self._inote = inote
        self.show = self._load_show(inote)
        self.episode = self._load_episode(inote)


    def _load_show(self, inote):
        """
        From the inote, determines the name of the show if it's included.

        Note: Even if ISDIR isn't in the string, it could be in the watch folder

        Params:
            inote: An inote string that this application was executed with

        Returns:
            the name of the show specified, or None.
        """

        # Get the delimiter and split the args. 
        delimiter = self._conf.get_delimiter()
        args = inote.split(delimiter)

        # If this is an ISDIR event (directory was created), then the third
        # argument (index 2) is the new folder
        # Isdir could be in the show name, so we only check the event log
        if "isdir" in args[1].lower(): 
            return args[2]

        # Isdir wasn't in the event, wihch means the episode file was created
        # However, the show name could be contained within the watch folder.
        # We can detremine this by removing the watch folder from the inote index 0
        # string and see if the string isn't length 0
        removed_watch_path = args[0].replace(self._conf.get_watch_folder(), "")
        if len(removed_watch_path) != 0:
            # sometihng besides the watch folder is there, so this is the show folder
            return removed_watch_path

        # Not a ISDIR and no show folder was in the watch folder, so this event is just
        # a new episode without a show specified. Thus, return None
        return None


    def _load_episode(self, inote):
        """
        From the inote, determines the name of episode if it's included.

        Note: The only case this wouldn't be is if an ISDIR event occurs.
        Otherwise, it's always the last argument in the splited inote (delimiter)

        Params:
            inote: An inote string that this application was executed with

        Returns:
            the name of the episode specified, or None.
        """

        # Get the delimiter and split the args.
        delimiter = self._conf.get_delimiter()
        args = inote.split(delimiter)

        # If this is an ISDIR event (directory was created), then no episode
        # will be specified.
        if "isdir" in args[1].lower():
            return None

        # Otherwise, because a file was made, it will always be the last argument
        # provided by inote (args split by delimiter)
        return args[2]


    # --------------------
    # Getters!
    # --------------------

    def get_show(self):
        """
        A getter method to return the show for the provided inote

        Returns;
            The show name as a string, or None if there wasn't a show
        """
        return self.show

    def get_episode(self):
        """
        A getter method to return the episode for the provided inote

        Returns:
            The episode name as a string, or None if not provided
        """
        return self.episode