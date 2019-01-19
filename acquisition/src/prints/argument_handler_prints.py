class ArgumentHandlerPrints:
    """
    This class stores all the various print statements used by ArgumentHandler

    Logger sets if printed or not.
    """

    def __init__(self, colors):

        self._colors = colors # printh.Colors() method

        # Some temporary, frequent-use variables
        endc = self._colors.ENDC

        # Notifying the user what notification was sent
        self.DISPLAY_INOTE = "[Argument] System Invocation: " + \
            self._colors.OKGREEN + "%s" + self._colors.ENDC


        # Show print statements ---------------------------------
        show_color = self._colors.LMAGENTA

        # Notifying the user what show was found, or none
        self.SHOW_LOADED = "[Argument] Show:" + show_color + "%s" + endc
        # Notifying the user that no show was contained in the argument.
        self.SHOW_NONE = "[Argument] Show: " + show_color + "None Provided" + endc


        # Show episode statements ---------------------------------
        episode_color = self._colors.LMAGENTA

        # Notifying the user what episode was found, or none
        self.EPISODE_LOADED = "[Argument] Episode: " + episode_color + "%s" + endc
        # Notifying the user that no episode was contained in the argument
        self.EPISODE_NONE = "[Argument] Episode: " + episode_color + "None Provided" + endc