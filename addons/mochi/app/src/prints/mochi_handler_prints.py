class MochiHandlerPrints:
    """
    Stores all the printing stuff used by MochiHandler

    Logger sets if printed or not.
    """

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use varialbes
        endc = colors.ENDC 
        prefix = "[Mochi] "
        mochi_color = colors.LMAGENTA

        self.MOCHI_START = prefix + "Starting Mochi snippets..."
        self.MOCHI_END = prefix + "Mochi snippet sequence completed."

        self.MOCHI_DISCORD_SEND = prefix + "Sending Mochis snippet to " + \
            mochi_color + "{}" + endc + "..." 

        self.SENDING_REQUEST_START = prefix + "Notifying " + mochi_color + "{}" + endc + \
            " with template " + mochi_color + "{}" + endc + "..."
        self.SENDING_REQUEST_SUCCESS = prefix + "Request to " + \
            mochi_color + "{}" + colors.OKGREEN + " successful" + endc
        self.SENDING_REQUEST_FAIL = prefix + "Request to " + \
            mochi_color + "{}" + colors.FAIL + " failed" + endc