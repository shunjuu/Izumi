
class RequestHandlerPrints:
    """
    This class stores all the various print statements used by RequestHandler
    """

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        # Frequent-use variables
        endc = colors.ENDC 
        prefix = "[Request] "

        # When elements are loaded
        loading_color = colors.LMAGENTA

        self.LOADED_SHOW = prefix + "Loaded show: " + \
            loading_color + "{}" + endc

        self.LOADED_EPISODE = prefix + "Loaded episode: " + \
            loading_color + "{}" + endc

        self.LOADED_FILESIZE = prefix + "Loaded filesize: " + \
            loading_color + "{}" + endc

        self.LOADED_SUB_TYPE = prefix + "Loaded sub type: " + \
            loading_color + "{}" + endc

        self.BAD_SUB_TYPE = prefix + colors.FAIL + "Error" + \
            endc + ": Sub type " + colors.LMAGENTA +  "{}" + \
            endc + " not in accepted types."