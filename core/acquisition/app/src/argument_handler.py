import sys
import os

import pprint as pp

# Print statements
from src.prints.argument_handler_prints import ArgumentHandlerPrints

class ArgumentHandler:
    """
    Not to be confused with ArgParser, this class is designed to handle
    extracting information from inotify-style strings.

    This class doesn't get any information from online, it just extracts 
    what it can from the argument.
    """

    def __init__(self, conf, printh, inote=None):
        """
        Args:
            conf: a ConfigHandler which already has the config.yml/json loaded.
            printh: A PrintHandler that should already be populated
        """

        self._conf = conf

        self._logger = printh.get_logger()
        self._prints = ArgumentHandlerPrints(printh.Colors())

        """
        Class variables
        """
        self._inote = None # The current _inote to process

        # Either of these could be none because ISDIR isn't guaranteed to happen
        self._show = None # The show name if provided, else None
        self._episode = None # The name of the episode if provided, else None

        # Load inote if it's provided
        if inote:
            self._load_inote(inote)


    def _load_inote(self, inote):
        """
        Loads a new inote into the class. It then automatically 
        sets the self._show and self._episode variables appropriately.

        Params:
            inote: An inote string that this application was executed with.
        """

        # Output
        self._logger.warning(self._prints.DISPLAY_INOTE.format(inote))

        self._inote = inote
        self._show = self._load_show(inote)
        self._episode = self._load_episode(inote)


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

            show = args[2]

            if show.endswith("/"): 
                show = show[:-1]

            self._logger.info(self._prints.SHOW_LOADED.format(show))
            return show

        # Isdir wasn't in the event, wihch means the episode file was created
        # However, the show name could be contained within the watch folder.
        # We can detremine this by removing the watch folder from the inote index 0
        # string and see if the string isn't length 0
        removed_watch_path = args[0].replace(self._conf.get_watch_folder(), "")
        if len(removed_watch_path) != 0:
            # something besides the watch folder is there, so this is the show folder

            # Remove the "/" at the end if there is one
            if removed_watch_path.endswith("/"):
                removed_watch_path = removed_watch_path[:-1]

            self._logger.info(self._prints.SHOW_LOADED.format(removed_watch_path))
            return removed_watch_path

        # Not a ISDIR and no show folder was in the watch folder, so this event is just
        # a new episode without a show specified. Thus, return None

        self._logger.info(self._prints.SHOW_NONE)
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
            self._logger.info(self._prints.EPISODE_NONE)
            return None

        # Otherwise, because a file was made, it will always be the last argument
        # provided by inote (args split by delimiter)
        self._logger.info(self._prints.EPISODE_LOADED.format(args[2]))
        return args[2]


    # --------------------
    # Getters!
    # --------------------

    @property
    def show(self):
        """
        A getter method to return the show for the provided inote
        Returns:
            The show name as a string, or None if there wasn't a show
            If there is a show, it will not have a "/" at the end.
        """
        return self._show

    @property
    def episode(self):
        """
        A getter method to return the episode for the provided inote
        Returns:
            The episode name as a string, or None if not provided
        """
        return self._episode
