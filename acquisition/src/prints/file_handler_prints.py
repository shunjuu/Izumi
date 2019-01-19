class FileHandlerPrints:
    """
    This class stores all the various print statements used by FileHandler

    Logger sets if printed or not.
    """

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use variables
        endc = colors.ENDC
        prefix = "[File] "

        # Episode Printouts
        episode_color = colors.LCYAN
        self.EPISODE_LOADED_ARG = prefix + "Loaded Episode: " + episode_color + \
            "{}" + endc
        self.EPISODE_LOADED_FOUND = prefix + "Found Episode: " + episode_color + \
            "{}" + endc
        self.EPISODE_LOADED_ERROR = prefix + "No episode was found. Now exiting..."
        # New Episode Printouts
        self.EPISODE_NEW_NAME = prefix + "New Episode Name: " + episode_color + \
            "{}" + endc

        # Show Printouts
        show_color = colors.LCYAN
        self.SHOW_LOADED_ARG = prefix + "Loaded Show: " + show_color + \
            "{}" + endc
        self.SHOW_LOADED_HISHA = prefix + "Found Show (Hisha): " + show_color + \
            "{}" + endc

        # Filesize Printouts
        fsize_color = colors.LCYAN
        self.FILESIZE_DISPLAY = prefix + "File size: " + fsize_color + \
            "{}B" + endc

        # Sub Type
        sub_color = colors.LCYAN
        self.SUB_TYPE = prefix + "Sub Type: " + sub_color + \
            "{}" + endc
