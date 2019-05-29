import sys
import os

import json
import yaml

import pprint as pp

import requests # For fetching web configs

# File Extension Definitions
YAML_EXT = ['.yaml', '.yml']
JSON_EXT = ['.json']


class ConfigHandler:
    """
    ConfigHandler deals with loading and extracting configurations. 

    This class does not print anything through the logger.
    """

    def __init__(self, cpath="config.yml"):
        """
        Args:
            cpath - A path that points to the config file. If not specified,
            the application will load the regular config.yml.
        """

        # Get the absolute path of the config.yml path for all use cases.
        cpath_abs = os.path.abspath(cpath)
        # Load the config into a dict Object
        initial_conf = self._load_local_config(cpath_abs)

        """
        Variables
        """
        self._web_config_url = None # The URL if a config will be loaded from the web
        self._conf = None # The real config to parse all other vars from
        self._web_conf_use = False # Whether or not using web-style conf

        self._watch_folder = None # The watch folder of the string

        self._destinations = None # A list of rclone destinations
        self._airing_folder = None # The name of an airing folder to store to
        self._rclone_flags = None # Flags used by rclone to determine its output

        self._encoders_always = None # The encoding endpoints, always
        self._encoders_sequential = None # The encoding endpoints, sequential
        self._notifiers_always = None # The notification endpoints, always
        self._notifiers_sequential = None # The notification endpoints, sequential
        self._distributors_always = None # The distribution endpoints, always
        self._distributors_sequential = None # The distribution endpoints, sequential

        self._name = None # The name of this application insance
        self._delimiter = None # The delimiter used by inotify !!IMPORTANT
        self._verbose = False # Whether or not we are printing verbosely

        self._logging_logfmt = None # The format string for the logger to use
        self._logging_datefmt = None # If logging strings include asctime (strftime format)

        # ---------------- #

        # First, we want to load the web config URL if it exists.
        self._web_config_url = self._load_web_config_url(initial_conf)
        # If it does exist, we want to open the URL 
        if self._web_config_url:
            # If there is a web url, then load it from here
            self._conf = self._load_conf_from_web(self._web_config_url)
            self._web_conf_use = True
        # Else load it from the regular file 
        else:
            self._conf = initial_conf
            self._web_conf_use = False

        # ---------------- #
        # Populate the rest of the variables now
        # ---------------- #
        self._watch_folder = self._load_watch_folder(self._conf, self._web_conf_use)

        self._destinations = self._load_destinations(self._conf, self._web_conf_use)
        self._airing_folder = self._load_airing_folder(self._conf, self._web_conf_use)
        self._rclone_flags = self._load_rclone_flags(self._conf, self._web_conf_use)

        self._encoders_always = self._load_endpoints_encoders_always(self._conf, self._web_conf_use)
        self._encoders_sequential = self._load_endpoints_encoders_sequential(self._conf, self._web_conf_use)
        self._notifiers_always = self._load_endpoints_notifiers_always(self._conf, self._web_conf_use)
        self._notifiers_sequential = self._load_endpoints_notifiers_sequential(self._conf, self._web_conf_use)
        self._distributors_always = self._load_endpoints_distributors_always(self._conf, self._web_conf_use)
        self._distributors_sequential = self._load_endpoints_distributors_sequential(self._conf, self._web_conf_use)

        self._name = self._load_system_name(self._conf, self._web_conf_use)
        self._delimiter = self._load_system_delimiter(self._conf, self._web_conf_use)
        self._verbose = self._load_system_verbose(self._conf, self._web_conf_use)
        
        self._logging_logfmt = self._load_logging_logfmt(self._conf, self._web_conf_use)
        self._logging_datefmt = self._load_logging_datefmt(self._conf, self._web_conf_use)

    # Getter methods

    @property
    def watch_folder(self):
        """Returns the watch folder, as a string. The path will end with a "/" """
        return self._watch_folder

    @property
    def destinations(self):
        """Returns the upload destinations, as a list of strings"""
        return self._destinations

    @property
    def airing_folder(self):
        """Returns the airing folder name as a String. Contains a "/" at the end"""
        return self._airing_folder

    @property
    def rclone_flags(self):
        """Returns the flags used by rclone as a single string."""
        return self._rclone_flags

    @property
    def encoders(self):
        """Returns the encoders as a tuple (always, sequential)"""
        return (self._encoders_always, self._encoders_sequential)
    
    @property
    def encoders_always(self):
        """Returns the always encoder endpoints as a list of dicts"""
        return self._encoders_always
    
    @property
    def encoders_sequential(self):
        """Returns the sequential encoder endpoints as a dict of list of dicts"""
        return self._encoders_sequential

    @property
    def notifiers(self):
        """Returns the notifiers as a tuple (always, sequential)"""
        return (self._notifiers_always, self._notifiers_sequential)
    
    @property
    def notifiers_always(self):
        """Returns the always notifier endpoints as a list of dicts"""
        return self._notifiers_always
    
    @property
    def notifiers_sequential(self):
        """Returns the sequential notifier endpoints as a dict of list of dicts"""
        return self._notifiers_sequential

    @property
    def distributors(self):
        """Returns the distributors as a tuple (always, sequential)"""
        return (self._distributors_always, self._distributors_sequential)
    
    @property
    def distributors_always(self):
        """Returns the always distributors endpoints as a list of dicts"""
        return self._distributors_always
    
    @property
    def distributors_sequential(self):
        """Returns the sequential distributors endpoints as a dict of list of dicts"""
        return self._distributors_sequential

    @property
    def name(self):
        """Returns the name for this application specified by the user"""
        return self._name
    
    @property
    def delimiter(self):
        """Returns the delimiter used by inotify as a string"""
        return self._delimiter

    @property
    def verbose(self):
        """Returns a boolean representing whether or not to verbose print"""
        return self._verbose

    @property
    def logging_logfmt(self):
        """Returns a string reprsentation for the logfmt"""
        return self._logging_logfmt

    @property
    def logging_datefmt(self):
        return self._logging_datefmt


    # Loading methods

    def _load_local_config(self, cpath_abs):
        """
        Loads the config path into a parsable dict.

        Args:
            cpath_abs: The absolute path of the config file, path only

        Returns: A dict representation of the config file.
        """

        # Determine if we're loading a YAML or JSON file
        _, file_ext = os.path.splitext(cpath_abs)

        if file_ext in YAML_EXT:
            with open(cpath_abs, 'r') as cfyml:
                try:
                    return yaml.full_load(cfyml)
                except:
                    pass
                    # TODO: print statement here for loading config error

        elif file_ext in JSON_EXT:
            with open(cpath_abs, 'r') as cfjson:
                try:
                    return json.load(cfjson)
                except:
                    pass
                    # TODO: print statement here for loading config error

        # If we've reached this point, then print some 
        # TODO: print statement for loading config error


    def _load_web_config_url(self, conf):
        """
        Loads the web config URL from the config.
        This is the ONLY function that doesn't have multiple behaviors 
            (between web and local)
 
        Args:
            conf: A dictionary representation of the Config file

        Returns: The string representing the web-config entry
        """
        return conf['web-config']


    def _determine_url_extension(self, url):
        """
        Determines the file extension from the URL of the web.
        Because we're not using headers, we need to manually scan the
        string itself.

        Args:
            url: The url of the web conf

        Returns: The extension of the url. Includes the "."
        """
        for ext in YAML_EXT:
            if url.endswith(ext):
                return ext

        for ext in JSON_EXT:
            if url.endswith(ext):
                return ext

        # TODO: Raise an exception if we reach this point cause no
        # suitable extension was found


    def _load_conf_from_web(self, url):
        """
        Retrieves the config from the web and returns it as a dict object

        Args:
            url: The url of the web conf. Should be a direct link to a 
            yaml or json file. 

        Returns: The web config, as a Dict object
        """

        # Figure out what extension we're working with
        file_ext = self._determine_url_extension(url)
        # Fetch the request itself
        webconf = requests.get(url)

        # Run it through YAML or JSON accordingly
        if file_ext in YAML_EXT:
            try:
                return yaml.load(webconf.text)
            except:
                pass
                # TODO: print statement here for loading config error

        elif file_ext in JSON_EXT:
            try:
                return json.loads(webconf.text)
            except:
                pass     
                # TODO: print statement here for loading config error

    def _load_watch_folder(self, conf, web):
        """
        Determines the watch folder for this application.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The watch folder string, which ends with a "/"

        Automatically returns "/watch" if Docker use is detected
        """

        # TODO: Return if web
        if web:
            pass

        # Return the local, since we're not using the web conf
        if 'DOCKER' not in os.environ:
            folder = conf['watch-folder']
        else:
            USAGE = bool(os.environ.get("DOCKER"))
            if USAGE:
                folder = "/watch"
            else:
                folder = conf['watch-folder']
                
        # And append a "/" if it's not added in by the user
        folder = folder if folder.endswith("/") else folder + "/"

        return folder


    def _load_airing_folder(self, conf, web):
        """
        Gets the name of "Airing" folder for new shows, and appends a "/" at the end
        if there isn't one already. Otherwise, if it's a blank string, simply 
        gets the Airing folder as is. (ending with / is for ease of building strings later.) 

        Params:
            conf: self._conf, which represents a dict object 
                of the loaded conf
            web: A boolean value which indicates if the web conf 
                is being used (default: local)

        Returns: The airnig folder string ending with "/", or an empty string
        """
        # TODO: Return if web
        if web:
            pass

        # Return the local, since we're not using the web conf
        airing = conf['uploading']['airing-folder-name']
        # Make sure it ends with a "/" if there's anything in airing
        if airing:
            if not airing.endswith("/"):
                airing = airing + "/"

        return airing


    def _load_rclone_flags(self, conf, web):
        """
        Determines the flags for rclone to use when uploading.

        Params:
            conf: self._conf, which represents a dict object 
                of the loaded conf
            web: A boolean value which indicates if the web conf 
                is being used (default: local)

        Returns: The flags specified as a string
        """

        # TODO: Return if web
        if web:
            pass

        # Return the local
        flags = conf['uploading']['rclone-flags']
        return flags

    def _load_destinations(self, conf, web):
        """
        Determines the rclone endpoints for files to be uploaded to.

        Params:
            conf: self._conf, which represents a dict object 
                of the loaded conf
            web: A boolean value which indicates if the web conf 
                is being used (default: local)

        Returns: A list of (watch folder) strings

        Affixes a "/" to the end of each config if it's missing.
        """
        if web:
            pass

        # Return the local, since we're not using the web conf
        folder = conf['uploading']['upload-destinations']

        # The length of the destinations list must be at least 1
        # Or else the uploader config is bad
        if len(folder) < 1:
            # TODO: print an error and exit
            sys.exit(1)

        # Make sure each destination ends with a "/"
        for dest in range(len(folder)):
            if not folder[dest].endswith("/"):
                folder[dest] += "/"

        return folder


    def _load_endpoints_encoders_always(self, conf, web):
        """
        Finds the ALWAYS encoder endpoints.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: A list of lists, where each inside list represents one endpoint
            entry. Index 0 is URL, Index 1 (optional) is an Authorization key.
        """
        if web:
            pass

        # Return from the local config
        return conf['endpoints']['encoders']['always']


    def _load_endpoints_encoders_sequential(self, conf, web):
        """
        Finds the SEQUENTIAL encoder endpoints.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: A list of list of lists. 
        For x in root list, y in x in order represents URLs in order to 
        try until a single request succeeds.
        Follows standard index 0/1 url/auth key(opt)
        """
        if web:
            pass

        # Return from the local config
        return conf['endpoints']['encoders']['sequential']


    def _load_endpoints_notifiers_always(self, conf, web):
        """
        Finds the ALWAYS notification endpoints.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: A list of lists, where each inside list represents one endpoint
            entry. Index 0 is URL, Index 1 (optional) is an Authorization key.
        """
        if web:
            pass

        # Return from the local config
        return conf['endpoints']['notifiers']['always']

    def _load_endpoints_notifiers_sequential(self, conf, web):
        """
        Finds the SEQUENTIAL notification endpoints.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: A list of list of lists. 
        For x in root list, y in x in order represents URLs in order to 
        try until a single request succeeds.
        Follows standard index 0/1 url/auth key(opt)
        """
        if web:
            pass

        # Return from the local config
        return conf['endpoints']['notifiers']['sequential']

    def _load_endpoints_distributors_always(self, conf, web):
        """
        Finds the ALWAYS notification endpoints.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: A list of lists, where each inside list represents one endpoint
            entry. Index 0 is URL, Index 1 (optional) is an Authorization key.
        """
        if web:
            pass

        # Return from the local config
        return conf['endpoints']['distributors']['always']

    def _load_endpoints_distributors_sequential(self, conf, web):
        """
        Finds the SEQUENTIAL notification endpoints.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: A list of list of lists. 
        For x in root list, y in x in order represents URLs in order to 
        try until a single request succeeds.
        Follows standard index 0/1 url/auth key(opt)
        """
        if web:
            pass

        # Return from the local config
        return conf['endpoints']['distributors']['sequential']

    def _load_system_name(self, conf, web):
        """
        Gets the instance name for this application

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The name, as a string
        """

        if web:
            pass

        # Return from the local config
        return conf['system']['name']

    def _load_system_delimiter(self, conf, web):
        """
        Finds the Delimiter set in Config and used by inotify

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The delimiter, as a string
        """
        if web:
            pass

        # Return from the local config
        return conf['system']['delimiter']

    def _load_system_verbose(self, conf, web):
        """
        Finds the Boolean Verbose option set in Config

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: A boolean value for verbosity usage
        """
        if web:
            pass

        # Return from the local config
        return conf['system']['verbose']

    def _load_logging_logfmt(self, conf, web):
        """
        Finds the logfmt string for logging set in Config

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The logfmt string
        """
        if web:
            pass

        # Return from the local config
        return conf['system']['logging']['logfmt']

    def _load_logging_datefmt(self, conf, web):
        """
        Finds the datefmt string for logging set in Config

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The datefmt string
        """
        if web:
            pass

        # Return from the local config
        return conf['system']['logging']['datefmt']
