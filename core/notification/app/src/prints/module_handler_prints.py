class ModuleHandlerPrints:
    """
    This class stores all the various print statements used by ModuleHandler
    """

    def __init__(self, colors):
        """  
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use variables
        endc = colors.ENDC
        prefix = "[Module] "

        hisha2a_color = colors.LYELLOW
        self.FETCHING_INFO_START = prefix + "Starting" + hisha2a_color + " information" + endc + " fetch" 
        self.FETCHING_INFO_END =prefix + hisha2a_color + "Information" + endc + " fetch successful"

        notify_color = colors.LYELLOW
        self.NOTIFY_ALL_START = prefix + "Starting all modules' notification sequences..."
        self.NOTIFY_ALL_END = prefix + "All modules' notification sequences completed"

        module_color = colors.LYELLOW
        self.MODULE_START = prefix + "Starting " + module_color + \
            "{}" + endc + " notification sequence"
        self.MODULE_END = prefix + "Completed " + module_color + "{}" + endc + " notification sequence"

        filter_color = colors.LYELLOW
        self.FILTER_NOT_USED = prefix + "Filters are not being used, proceeding"
        self.FILTER_SHOW_NOT_FOUND = prefix + "Show " + filter_color + "{}" + endc + \
            " not found in any filter configurations"
        self.FILTER_FOUND = prefix + "Found " + filter_color + "{}" + endc + \
            " in " + filter_color + "{}" + endc + " profile " + filter_color + "{}" + endc + \
            " by " + filter_color + "{}" + endc + ", proceeding"