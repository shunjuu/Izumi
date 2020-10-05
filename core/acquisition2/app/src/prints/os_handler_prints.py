
class OSHandlerPrints:
    """
    This class stores all the various print statements used by NetworkHandler
    """

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use variables
        endc = colors.ENDC
        prefix = "[OS] "

        # FS Replication Prints
        fs_color = colors.ORANGE
        # For FS replica creation
        self.FS_PATH_CREATION = prefix + "Created replica filesystem at " + \
            fs_color + "{}" + endc
        # For hard linking time
        self.FS_PATH_LINK_1 = prefix + "Linking " + fs_color + "{}" + endc + " -->"
        self.FS_PATH_LINK_2 = prefix + "--> to " + colors.OKGREEN + "{}" + endc

        # Temporary Directory Prints
        temp_dir_color = colors.ORANGE
        # Print statemnet when the temp dir is made
        self.TEMP_DIR_CREATE_SUCCESS = prefix + "Created temporary directory at " + \
            temp_dir_color + "{}" + endc
        self.TEMP_DIR_CREATE_ERROR = prefix + \
            "An error occured while creating the temporary directory, exiting..."

        # Source file
        # For when the source file is found
        src_color = colors.ORANGE
        self.SOURCE_FILE_FOUND = prefix + "Found source file at " + \
            src_color + "{}" + endc

        # Rclone uploading
        rclone_color = colors.LCYAN
        self.RCLONE_UPLOAD_START = prefix + "Uploading to " + \
            rclone_color + "{}" + endc
        self.RCLONE_UPLOAD_END = prefix + "Completed uploading to " + \
            rclone_color + "{}" + endc

        # Cleanup
        cleanup_color = colors.WARNING
        # Temp dir cleaning
        self.CLEANUP_TEMP_ALL = prefix + "Cleared temporary directory at " + \
            cleanup_color + "{}" + endc
        self.CLEANUP_TEMP_ALL_ERROR = prefix + "Error removing temporary directory at " + \
            cleanup_color + "{}" + endc
        # Cleaning up when source was ISDIR
        self.CLEANUP_SRC_OBJ_ISDIR = prefix + "Removed source directory at " + \
            cleanup_color + "{}" + endc
        self.CLEANUP_SRC_OBJ_ISDIR_ERROR = prefix + "Error removing source directory at " + \
            cleanup_color + "{}" + endc
        # Cleaning up when source file provided without folder
        self.CLEANUP_SRC_OBJ_FILE_ONLY = prefix + "Removed source file at " + \
            cleanup_color + "{}" + endc
        # If show was provided in path, removing that path
        self.CLEANUP_SRC_OBJ_FOLDER_PROVIDED = prefix + "Removed source folder at " + \
            cleanup_color + "{}" + endc