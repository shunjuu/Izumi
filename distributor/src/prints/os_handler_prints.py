class OSHandlerPrints:
    """
    This class stores all the various print statements used by OSHandler

    Logger sets if printed or not.
    """

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        # Temporary, frequent-use variables
        endc = colors.ENDC 
        prefix = "[OS] "

        # Temporary Directory Prints
        temp_dir_color = colors.ORANGE
        # Print statemnet when the temp dir is made
        self.TEMP_DIR_CREATE_SUCCESS = prefix + "Created temporary directory at " + \
            temp_dir_color + "{}" + endc
        self.TEMP_DIR_CREATE_ERROR = prefix + \
            "An error occured while creating the temporary directory, exiting..."

        # Download colors
        rclone_color = colors.BLUE
        episode_color = colors.GREEN
        self.EPISODE_FOUND = prefix + "Found " + episode_color + "{}" + endc + \
            " in " + rclone_color + "{}" + endc
        self.EPISODE_NOT_FOUND = prefix + colors.FAIL + "Error" + endc + \
            ": " + episode_color + "{}" + endc + " not found in any sources."
        self.DOWNLOAD_START = prefix + "Now starting download [" + \
            episode_color + "{}" + endc + "] from [" + rclone_color + "{}" + endc + "]..."
        self.DOWNLOAD_COMPLETE = prefix + "Completed download [" + \
            episode_color + "{}" + endc + "] from [" + rclone_color + "{}" + endc + "]..."

        # RequestHandler's hardsub searching
        reqh_fail_color = colors.FAIL
        self.REQH_SOFTSUB = prefix  + "Sub type " + reqh_fail_color + "{}" + endc + \
            " not recognized, exiting..."

        # Upload colors
        upload_color = colors.GREEN
        self.UPLOAD_REMOVE_SRC_FILE = prefix + "Removed source file [" + \
            upload_color + "{}" + endc + "]"
        self.UPLOAD_REMOVE_SRC_FILE_FAIL = prefix + "Failed to remove source file [" + \
            upload_color + "{}" + endc + "]"
        self.UPLOAD_START = prefix + "Starting upload to " + \
            upload_color + "{}" + endc
        self.UPLOAD_COMPLETE = prefix + "Completed upload to " + \
            upload_color + "{}" + endc

        # Cleanup
        temp_color = colors.ORANGE
        self.DELETE_TEMP_FOLDER = prefix + "Deleting the temporary folder at " + \
            temp_color + "{}" + endc
        self.DELETE_TEMP_FOLDER_SUCCESS = prefix + colors.GREEN + "Success" + \
            endc + ": Deleted the temporary folder at " + \
            temp_color + "{}" + endc
        self.DELETE_TEMP_FOLDER_FAIL = prefix + colors.FAIL + "Failure:" + endc + \
            "Could not delete the temporary folder at " + \
            temp_color + "{}" + endc