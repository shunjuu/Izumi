class AuthHandlerPrints:
    """
    This class stores all the various print statements used by AuthHandler

    Logger sets if printed or not.
    """

    def __init__(self, colors):
        """
        Params:
            colors - print_handler.Colors() module
        """

        # Some temporary, frequent-use varialbes
        endc = colors.ENDC 
        prefix = "[Auth] "

        # When AuthHandler is refreshing the file
        self.AUTH_REFRESH = prefix + "Refreshing auth file..."
        self.AUTH_REFRESH_SUCCESS = prefix + "Refreshed auth from " + \
            colors.LCYAN + "{}" + endc

        # Local Auth Loading
        local_color_success = colors.LCYAN
        local_color_error = colors.FAIL
        self.LOCAL_AUTH_YAML_SUCCESS = prefix + "Successfully loaded a local YAML auth file from " + \
            local_color_success + "{}" + endc
        self.LOCAL_AUTH_YAML_ERROR = prefix + "Error while attempting to load a local YAML auth file from " + \
            local_color_error + "{}" + endc
        self.LOCAL_AUTH_JSON_SUCCESS = prefix + "Successfully loaded a local JSON auth file from " + \
            local_color_success + "{}" + endc
        self.LOCAL_AUTH_JSON_ERROR = prefix + "Error while attempting to load a local JSON auth file from " + \
            local_color_error + "{}" + endc

        # Which authorization is matched
        authorized = colors.OKGREEN
        failure = colors.FAIL
        self.AUTH_SUCCESS_NO_ENTRIES_NO_KEY = prefix + authorized + "Success: " + endc + \
            "Request authorized - no auth entries and no key provided"
        self.AUTH_SUCCESS_YES_ENTRIES_YES_KEY = prefix + authorized + "Success: " + endc + \
            "Request authorized - auth entries exist and a matching key was provided"
        self.AUTH_FAILURE_YES_ENTRIES_NO_KEY = prefix + failure + "Failure: " + endc + \
            "Request denied - auth entries exist but no key provided"
        self.AUTH_FAILURE_YES_ENTRIES_NO_MATCH = prefix + failure + "Failure: " + endc + \
            "Request denied - auth entries exist but no key matched"
        self.AUTH_FAILURE_NO_ENTRIES_YES_KEY = prefix + failure + "Failure: " + endc + \
            "Request denied - no auth entries but key was provided"

        self.AUTH_FAILURE_NO_JSON_OR_YAML = prefix + failure + "Failure: " + endc + \
            "Request denied - auth config file is neither json nor yaml"