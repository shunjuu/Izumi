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
            the application will load the regular config.yml
        """

        # Get the absolute path of the config.yml path for all use cases.
        cpath_abs = os.path.abspath(cpath)
        # Load the config into a dict object
        initial_conf = self._load_local_config(cpath_abs)

        """
        Variables
        """

        # First, we want to load the web config URL if it exists.

        # self._web_config_url: The URL if a config will be loaded from the web
        # self._conf: The real config to parse all other vars from
        # self._web_conf_use: Whether or not web conf is being used
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

        # The port Flask will listen to
        self._listen_port = self._load_listen_port(self._conf, self._web_conf_use)

        # The flags to be used for encoding videos
        self._encode_encode_flags = self._load_encode_encode_flags(self._conf, self._web_conf_use) 
        # Number of encoding jobs that can run at once 
        self._encode_encode_jobs = self._load_encode_encode_jobs(self._conf, self._web_conf_use)

        # The list of rclone sources to dl from
        self._download_download_sources = self._load_download_download_sources(self._conf, self._web_conf_use)
        # The name of the softsub folder name
        self._download_softsub_folder = self._load_download_softsub_folder(self._conf, self._web_conf_use)
        # Flags for rclone to use when downloading
        self._download_rclone_flags = self._load_download_rclone_flags(self._conf, self._web_conf_use)
        # List of rclone dests to upload to
        self._upload_destinations = self._load_upload_destinations(self._conf, self._web_conf_use)
        # The name of the hardsub folder to upload to
        self._upload_hardsub_folder = self._load_upload_hardsub_folder(self._conf, self._web_conf_use)
        # Flags for rclone to use when downloading
        self._upload_rclone_flags = self._load_upload_rclone_flags(self._conf, self._web_conf_use)
        # The Always endpoints used by the system
        self._endpoints_always = self._load_endpoints_always(self._conf, self._web_conf_use)
        # The Sequential endpoints used by the system
        self._endpoints_sequential = self._load_endpoints_sequential(self._conf, self._web_conf_use)
        # The name of this application insance
        self._name = self._load_system_name(self._conf, self._web_conf_use)
        # Whether or not we are printing verbosely
        self._verbose = self._load_system_verbose(self._conf, self._web_conf_use)
        # The format string for the logger to use
        self._logging_logfmt = self._load_logging_logfmt(self._conf, self._web_conf_use)
        # If logging strings include asctime (strftime format)
        self._logging_datefmt = self._load_logging_datefmt(self._conf, self._web_conf_use)


    @property
    def listen_port(self):
        """Returns the port for flask to listen to, as an integer"""
        return self._listen_port
    
    @property
    def encode_encode_flags(self):
        """Returns the flags to be used by rclone as a string"""
        return self._encode_encode_flags
    
    @property
    def encode_encode_jobs(self):
        """Returns the number of encoding jobs run simultaneously as an int."""
        return self._encode_encode_jobs

    @property
    def download_download_sources(self):
        """Returns the rclone download sources list, each ending with "/" """
        return self._download_download_sources
    
    @property
    def download_softsub_folder(self):
        """Returns the softsub folder as a string, with "/" ending"""
        return self._download_softsub_folder

    @property
    def download_rclone_flags(self):
        """Returns the download rclone flags as a string"""
        return self._download_rclone_flags
    
    @property
    def upload_destinations(self):
        """Returns the upload destinations as a list of strings, all ending with "/" """
        return self._upload_destinations

    @property
    def upload_hardsub_folder(self):
        """Returns the upload hardsub folder, ending with a "/" """
        return self._upload_hardsub_folder
    
    @property
    def upload_rclone_flags(self):
        """Returns the string representing the upload rclone flags"""
        return self._upload_rclone_flags

    @property
    def endpoints_always(self):
        """Returns the always endpoints"""
        return self._endpoints_always
    
    @property
    def endpoints_sequential(self):
        """Returns the sequential endpoints"""
        return self._endpoints_sequential
    
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
    def verbose(self):
        """Returns a boolean representing whether or not to verbose print"""
        return self._verbose
    
    @property
    def logging_logfmt(self):
        """Returns a string representation for the logfmt"""
        return self._logging_logfmt
    
    @property
    def logging_datefmt(self):
        """Returns a string representation for the datefmt"""
        return self._logging_datefmt
 
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

    def __determine_url_extension(self, url):
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
        file_ext = self.__determine_url_extension(url)
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


    def _load_listen_port(self, conf, web):
        """
        Retrieve the port for Flask to listen to.
        If the app is detected to be Docker, returns port 80

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The port, as an integer
        """

        if web:
            pass

        # If runtime is Docker, then return 80 by default
        if 'DOCKER' in os.environ and bool(os.environ.get("DOCKER")):
            return 80

        # Return from the local config
        return int(conf['listen-port'])

    def _load_encode_encode_flags(self, conf, web):
        """
        Retrive the flags for ffmpeg to use.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The flags as a string
        """

        if web:
            pass

        return conf['encoding']['encode-flags']

    def _load_encode_encode_jobs(self, conf, web):
        """
        Retrives the number of jobs that a single encoder can run simultaneously.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The number of encoding jobs, as an integer.
        """

        if web:
            pass

        count = int(conf['encoding']['encode-jobs'])
        if count < 1:
            # There's an error here
            sys.exit(1)

        return count

    def _load_download_download_sources(self, conf, web):
        """
        Gets the list of rclone download sources.

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: A list of strings that are the rclone sources
        All sources end with "/"
        """

        if web:
            pass

        # Return from the local config
        folder = conf['downloading']['download-sources']

        # The length of the folders must be at least 1 
        # or else the config is bad
        if len(folder) < 1:
            # TODO: print an error and exit
            sys.exit(1)

        # Make sure each destination ends with a "/"
        for src in range(len(folder)):
            if not folder[src].endswith("/"):
                folder[src] += "/"

        return folder


    def _load_download_softsub_folder(self, conf, web):
        """
        Gets the name of the softsub folder

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns the folder name, ending with a "/"
        """

        if web:
            pass

        folder = conf['downloading']['softsub-folder-name']

        if folder:
            if not folder.endswith("/"):
                folder += "/"

        return folder


    def _load_download_rclone_flags(self, conf, web):
        """
        Gets the rclone flags used by the downloader

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns the rclone flags as a string
        """

        if web:
            pass

        return conf['downloading']['rclone-flags']

    def _load_upload_destinations(self, conf, web):
        """
        Gets the reclone upload destinations by the downloader


        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns the rclone upload locations, each ending with a "/"
        """

        if web:
            pass

        folder = conf['uploading']['upload-destinations']

        # The length of the folders must be at least 1 
        # or else the config is bad
        if len(folder) < 1:
            # TODO: print an error and exit
            sys.exit(1)

        # Make sure each destination ends with a "/"
        for dest in range(len(folder)):
            if not folder[dest].endswith("/"):
                folder[dest] += "/"

        return folder       

    def _load_upload_hardsub_folder(self, conf, web):
        """
        Gets the name of the hardsub folder

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns the hardsub folder ending with a "/"
        """

        if web:
            pass

        folder = conf['uploading']['hardsub-folder-name']

        if folder:
            if not folder.endswith("/"):
                folder += "/"

        return folder

    def _load_upload_rclone_flags(self, conf, web):
        """
        Gets the rclone flags to be used when uploading

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns the rclone flags as a string
        """

        if web:
            pass

        return conf['uploading']['rclone-flags']

    def _load_endpoints_always(self, conf, web):
        """
        Loads the Always endpoints from the config

        Params:
            conf: self._conf, a dict object of the loaded conf
            web: a boolean value indicating if web conf is being used

        Returns: A list of dicts, each entry being an endpoint
        """ 
        if web:
            pass

        # Return from the local config
        return conf['endpoints']['always']

    def _load_endpoints_sequential(self, conf, web):
        """
        Loads the Sequential endpoints from the config

        Params:
            conf: self._conf, a dict object of the loaded conf
            web: a boolean value indicating if web conf is being used

        Returns: A dict of lists of dicts
        """
        if web:
            pass

        # Return from the local config
        return conf['endpoints']['sequential']

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

