class FBChatModulePrints:
    """
    This class stores various print statements used by FBChatModule
    """

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        endc = colors.ENDC
        prefix = "[FBChat] "

        self.DEV_ENABLED = prefix + "Dev mode " + colors.GREEN + "enabled" + endc
        self.DEV_DISABLED = prefix + "Dev mode " + colors.GREEN + "disabled" + endc

        fb_color = colors.BLUE
        self.SENDING_TO = prefix + "Sending notification to " + fb_color + "{}" + endc + \
            " with template " + fb_color + "{}" + endc + "..."