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

    Observe there are two types of inputs:
    ...folder/,CREATE,file.mkv
    ...path/,"CREATE,ISDIR",folder_name

    This method returns the first if given so, and alters the second to
    become the first. Note that the list of files array must be length 1.
    This is becase:
        1. If the folder already exists, the new dir will not be invoked
        2. Any other files should already have been deleted prior to invoke
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
        
        # args[0] is the path up to the folder, args[3] is the name of the folder itself
        # folder name is args[3], not args[2], because extra comma is inserted between
        # CREATE,ISDIR, increasing the array length by 1
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


def convert_inote_to_list(inote):
    """
    This converts the inotifywait string returned in fix_args()
    to an array for the rest of the program to use.

    Note we need this method because if shows contain a "comma" in the name,
    str.split(',') will split on that too, in which case we need to reconnect
    the show names.
    """

    args = inote.split(',')

    # Copy over the first two argument
    new_args = [None] * 2
    new_args[0] = args[0]
    new_args[1] = args[1]



def clean_filename(filename, ext):
    """
    Returns a str, which is the new filename for a file,
    i.e., [HorribleSubs] Grand Blue - 01 [1080p].mkv returns
    Grand Blue - 01 [1080p].mkv

    Requires anitopy to parse.

    Params:
    - filename: The original video's filename
    - ext: The new extension of the cleaned filename
    """

    p = anitopy.parse(filename)
    new_file = p['anime_title'] + " - " + p['episode_number']

    # If it's uncensored, we want to mark it
    if 'other' in p and 'uncensored' in p['other'].lower():
        new_file += " (Uncensored)"

    # There may be no video resolution
    if 'video_resolution' in p:
        new_file = new_file + " [" + p['video_resolution'] + "]"

    new_file += ext
    return new_file
                




print(fix_args(sys.argv[1], load_config()))

