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

def main():

    inote = sys.argv[1]

    try:
        c = ConfigHandler("/conf/config.yml")
        p = PrintHandler(c)
        a = ArgumentHandler(c, p, inote)
        f = FileHandler(c, a, p, inote)
        n = NetworkHandler(c, f, p)
    except:
        pass

    try:
        o = OSHandler(c, a, f, p)
        o.create_temp_replica_fs()
        o.upload()

        n.notify_encoders()
        n.notify_notifiers()
        n.notify_distributors()

    except:
        pass

    finally:
        o.cleanup()

if __name__ == "__main__":
    main()
