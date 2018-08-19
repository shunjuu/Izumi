import sys, os
import pprint as pp

from subprocess import call
from time import sleep
from shlex import quote

import requests
import json, yaml

import anitopy

def load_config():
    """
    Loads the config.yml file into a dict.
    """

    with open("config.yml", 'r') as conf:
        try:
            return yaml.load(conf)
        except:
            print("An exception occured while loading the config.")
            sys.exit(1)


def fix_args(inote, conf):
    """
    Function that will parse the inotifywatch strings sent to the machine.
    If new arg is a directory, it will "fix" the argument and return it.

    Params:
        inote: An inotifywait/wait style string
        runtype: Either "downloader" or "encoder"
    """

    print("Arg: " + inote)
    print()

    args = inote.split(',')

    # The most standard case: A new file is presented, devoid of folder
    if 'isdir' not in inote.lower():

        print("A regular file was detected.")
        new_filename = args[2]

        try:
            if new_filename.endswith(".meta"):
                print("Detected a meta file, ignoring...")
                sys.exit(0)
        except:
            print("Error when scanning for meta file")
            pass

        print("Not a meta file, returning the argument as is.")
        return inote

    # A more common case, where the new directory is linked in.
    elif 'isdir' in inote:
        print("Detected a new directory was made.")

        # If we're running anything but a downloader, we need to ignore dirs.
        # Only the downloader needs to scan the dir (for ruTorrent)
        if conf['type'].lower() != "downloader":
            print("Runtype is not a downloader. Exiting...")
            sys.exit(0)
        
        path = args[0] + args[3] + "/"

        # Get all the files in the new dir, there should only be a single .mkv softlink
        files = os.listdir(path)
        files = [f for f in files if f.endswith(".mkv")]

        # Make sure we only have one file
        if len(files) != 1:
            print("Detected more than a single file in the directory.")
            sys.exit(1)

        new_inote = path + ",CREATE," + files[0]
        print("Returning: " + new_inote, end="\n\n")
        return new_inote

                




print(sys.argv)

