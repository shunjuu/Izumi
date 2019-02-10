class DiscordWebhookModulePrints:
    """
    This class stores all the various print statements used by 
    DiscordWebhookModule
    """

    def __init__(self, colors):
        """  
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use variables
        endc = colors.ENDC
        prefix = "[DiscordWebhook] "

        self.DEV_ENABLED = prefix + "Dev mode " + colors.GREEN + "enabled" + endc
        self.DEV_DISABLED = prefix + "Dev mode " + colors.GREEN + "disabled" + endc

        req_color = colors.BLUE
        template_color = colors.LMAGENTA
        error_color = colors.FAIL
        self.SENDING_REQUEST_START = prefix + "Notifying " + req_color + "{}" + endc + \
            " with template " + template_color + "{}" + endc + "..."
        self.SENDING_REQUEST_SUCCESS = prefix + "Request to " + \
            req_color + "{}" + colors.OKGREEN + " successful" + endc
        self.SENDING_REQUEST_FAIL = prefix + "Request to " + \
            req_color + "{}" + error_color + " failed" + endc