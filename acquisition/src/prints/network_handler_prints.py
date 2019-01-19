
class NetworkHandlerPrints:
    """
    This class stores all the various print statements used by NetworkHandler
    """

    def __init__(self):

        # Print Statements

        # Sending requests
        self.SENDING_REQUEST = "Sending request to %s%s%s..."
        self.SENDING_REQUEST_SUCCESS = "Request to %s%s%s was successful."
        self.SENDING_REQUEST_FAIL = "Request to %s%s%s failed."

        # Sending Group Bodies
        self.GROUP_ENCODERS = "Now sending requests to %sencoders%s."
        self.GROUP_NOTIFIERS = "Now sending requests to %snotifiers%s."
        self.GROUP_DISTRIBUTORS = "Now sending requests to %sdistributors%s."

        # Always Bodies
        self.BODY_ALWAYS = "Working on %sAlways%s requests."
        self.BODY_SEQUENTIAl = "Working on %sSequential%s requests."

        # Warning messages
        self.WARNING_BAD_CODE = "Request to %s%s%s failed due to a bad response code (%s)."

        # Error messages