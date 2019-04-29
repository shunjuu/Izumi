"""
U1 Acquisition handles dealing with new episodes moved into a watch folder.
"""

import sys
import os

from src.config_handler import ConfigHandler
from src.argument_handler import ArgumentHandler
from src.file_handler import FileHandler
from src.network_handler import NetworkHandler
from src.os_handler import OSHandler
from src.print_handler import PrintHandler

from time import sleep

def _get_config_handler():
    """ 
    Gets the config path based on if Docker is used or not
    Checks environment for DOCKER='true' 
    Returns appropriate ConfigHandler
    """
    if 'DOCKER' not in os.environ:
        return ConfigHandler()
    else:
        USAGE = bool(os.environ.get("DOCKER"))
        if USAGE: 
            return ConfigHandler("/src/config.yml")
        else: 
            return ConfigHandler()

def main():

    inote = sys.argv[1]

    try:

        c = _get_config_handler()
        p = PrintHandler(c)
        a = ArgumentHandler(c, p, inote)
        f = FileHandler(c, a, p, inote)
        n = NetworkHandler(c, f, p)

        o = OSHandler(c, a, f, p)
        o.create_temp_replica_fs()
        o.upload()

        n.notify_encoders()
        n.notify_notifiers()
        n.notify_distributors()

    except Exception as e:
        print(e)
        pass

    finally:
        o.cleanup()

    print()

if __name__ == "__main__":
    main()
