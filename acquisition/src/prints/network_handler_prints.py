
class NetworkHandlerPrints:
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
        prefix = "[Network] "

        # Sending Request Printouts
        sending_color = colors.BLUE
        self.SENDING_REQUEST = prefix + "Sending request to: " + \
            sending_color + "{}" + endc
        self.SENDING_REQUEST_SUCCESS = prefix + "Request to " + \
            sending_color + "{}" + colors.OKGREEN + " successful" + endc

        # Errors for Requests
        error_color = colors.FAIL
        self.SENDING_REQUEST_FAIL = prefix + "Request to " + \
            sending_color + "{}" + error_color + " failed" + endc
        self.SENDING_REQUEST_CONNECTION_ERROR = prefix + error_color + \
            "Failed to connect to the server, please retry." + endc
        self.SENDING_REQUEST_SCHEMA_ERROR = prefix + "URL " + \
            error_color + "{}" + endc + " is missing schema (http/https)"
        self.SENDING_REQUEST_TIMEOUT_ERROR = prefix + "Timeout occured for " + \
            error_color + "{}" + endc
        self.SENDING_REQUEST_BAD_CODE = prefix + "Response from " + \
            error_color + "{}" + endc + " returned bad response code " + \
            error_color + "{}" + endc

        # Sending Group Bodies
        group_color = colors.BLUE
        group_base = prefix + "Now sending requests to " + group_color + "{}" + endc
        self.GROUP_ENCODERS = group_base.format("encoders")
        self.GROUP_NOTIFIERS = group_base.format("notifiers")
        self.GROUP_DISTRIBUTORS = group_base.format("distributors")

        # Always Bodies
        body_color = colors.BLUE
        body_base = prefix + "Working on " + body_color + "{}" + endc + "..."
        self.BODY_ALWAYS = body_base.format("Always")
        self.BODY_SEQUENTIAL = body_base.format("Sequential")
