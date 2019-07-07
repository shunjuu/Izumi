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
        # Which kinds of extensions Mochi accepts
        self._mochi_sub_types = self._load_mochi_sub_types(self._conf, self._web_conf_use)
        # Webhooks for Mochi to ping to
        self._mochi_discord_webhooks = self._load_mochi_discord_webhooks(self._conf, self._web_conf_use)
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
        # The route that the Flask server will listen on
        self._route = self._load_route(self._conf, self._web_conf_use)


    @property
    def listen_port(self):
        """Returns the port for flask to listen to, as an integer"""
        return self._listen_port

    @property
    def mochi_sub_types(self):
        return self._mochi_sub_types
    
    @property
    def mochi_discord_webhooks(self):
        """Returns the Mochi disord webhooks as a cleaned list"""
        return self._mochi_discord_webhooks
    
    @property
    def endpoints_always(self):
        """Returns the always endpoints"""
        return self._endpoints_always
    
    @property
    def endpoints_sequential(self):
        """Returns the sequential endpoints"""
        return self._endpoints_sequential

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
        """Returns a string reprsentation for the logfmt"""
        return self._logging_logfmt

    @property
    def logging_datefmt(self):
        """Returns a string reprsentation for the datefmt"""
        return self._logging_datefmt

    @property
    def route(self):
        """The route flask will listen on"""
        return self._route

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
                except Exception as e:
                    print(e)
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

    def _load_mochi_sub_types(self, conf, web):
        """
        Which kind of sub types is Mochi okay with?!
        Options: hardsub or softsub

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: A list of extensions Mochi will process
        """
        if web:
            pass

        sub_types = conf['mochi']['sub-types']
        for i in range(len(sub_types)):
            sub_types[i] = sub_types[i].lower()

        return sub_types
    
    def _load_mochi_discord_webhooks(self, conf, web): 
        """
        Loads all the Discord webhooks for Mochi to ping to

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The list of webhooks, cleaned:
            base will end with a '/'
        """

        if web:
            pass

        webhooks = conf['mochi']['discord-webhooks']

        for i in range(len(webhooks)):

            curr = webhooks[i]
            if "name" not in curr or not curr['name']:
                raise Exception("Webhook should have a name")
            if "url" not in curr or not curr['url']:
                raise Exception("Webhook needs a Discord URL")
            if "base" not in curr or not curr['base']:
                raise Exception("Webhook needs a base")

            if not curr['base'].endswith("/"):
                webhooks[i]['base'] = webhooks[i]['base'] + "/"

        return webhooks

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

    def _load_route(self, conf, web):
        """
        Loads the route that Flask will listen on

        Params:
            conf: self._conf, which represents a dict object
                of the loaded conf
            web: A boolean value which indicates if the web conf
                is being used (default: local)

        Returns: The route, as a string with a / appended before it
        """
        if web:
            pass

        route = conf['system']['route']
        if not route.startswith("/"):
            route = "/" + route

        # Return from the local config
        return route
        