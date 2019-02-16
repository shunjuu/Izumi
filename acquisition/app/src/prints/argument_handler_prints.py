class ArgumentHandlerPrints:
    """
    This class stores all the various print statements used by ArgumentHandler

    Logger sets if printed or not.
    """

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use variables
        endc = colors.ENDC
        prefix = "[Argument] "

        # Notifying the user what notification was sent
        self.DISPLAY_INOTE = prefix + "System Invocation: " + \
            colors.OKGREEN + "{}" + endc


        # Show print statements ---------------------------------
        show_color = colors.LMAGENTA

        # Notifying the user what show was found, or none
        self.SHOW_LOADED = prefix + "Show: " + show_color + "{}" + endc
        # Notifying the user that no show was contained in the argument.
        self.SHOW_NONE = prefix + "Show: " + show_color + "None Provided" + endc


        # Show episode statements ---------------------------------
        episode_color = colors.LMAGENTA

        # Notifying the user what episode was found, or none
        self.EPISODE_LOADED = prefix + "Episode: " + episode_color + "{}" + endc
        # Notifying the user that no episode was contained in the argument
        self.EPISODE_NONE = prefix + "Episode: " + episode_color + "None Provided" + endc