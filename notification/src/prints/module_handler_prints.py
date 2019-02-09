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
