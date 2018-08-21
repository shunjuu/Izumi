import sys, os
import pprint as pp

from subprocess import call
from time import sleep
from shlex import quote

import requests
import json, yaml 

import anitopy 

class colors:
    """
    Shell based colors for colored printing!
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    CYAN = '\033[0;36m'
    ORANGE = '\033[0;33m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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
    ...folder/,CREATE,file.mkv ...path/,"CREATE,ISDIR",folder_name

    This method returns the first if given so, and alters the second to
    become the first. Note that the list of files array must be length 1.
    This is becase:
        1. If the folder already exists, the new dir will not be invoked
        2. Any other files should already have been deleted prior to invoke
    """

    # Get the delimiter for the inote string passed in
    inote_delim = conf['sys']['delimiter']
    args = inote.split(inote_delim)

    # The most standard case: A new file is presented, devoid of folder
    if 'isdir' not in inote.lower():

        print(colors.CYAN + "INFO: " + colors.ENDC + 
                colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
                "Detected a regular, non-directory file object was created.")

        # The name of the file that was JUST MADE.
        # (We assume the delimiter is always working properly.)
        new_filename = args[2]

        try:
            if new_filename.endswith(".meta"):
                print(colors.FAIL + "FAIL: " + colors.ENDC + 
                        colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
                        "The new file created was a meta file. Ignoring the file and exiting.")
                sys.exit(1)

        except SystemExit:
            print()
            sys.exit(1)

        print(colors.CYAN + "INFO: " + colors.ENDC +
                colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
                "New file is " + colors.OKGREEN + "not" + colors.ENDC + " " +
                "a meta file.")
        
        print(colors.CYAN + "INFO: " + colors.ENDC + 
                colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
                "Returning unmodified inote: " + 
                "\"" + colors.WARNING + inote + colors.ENDC + "\"")

        print()
        return inote

    # A more common case, where the new directory is linked in.
    elif 'isdir' in inote.lower():
        print(colors.CYAN + "INFO: " + colors.ENDC +
                colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
                "Detected a new directory was made.")

        # If we're running anything but a downloader, we need to ignore dirs.
        # Only the downloader needs to scan the dir (for ruTorrent)
        if conf['type'].lower() != "downloader":
            print(colors.FAIL + "FAIL: " + colors.ENDC +
                    colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
                    "The runtype is not Downloader. Exiting the system...")
            print()
            sys.exit(0)

        else:
            print(colors.CYAN + "INFO: " + colors.ENDC + 
                    colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
                    "The runtype is Downloader. Proceeding to scan the directory for file(s).")
        
        # args[0] is the path up to the folder, args[3] is the name of the folder itself
        # folder name is args[3], not args[2], because extra comma is inserted between
        # CREATE,ISDIR, increasing the array length by 1
        # Update: args[2] instead of args[3] due to changes in delimiting to ||
        path = args[0] + args[2] + "/"
        print(colors.CYAN + "INFO: " + colors.ENDC + 
                colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
                "Scanning: " + 
                colors.WARNING + "\"" + path + "\"" + colors.ENDC)

        # Get all the files in the new dir, there should only be a single .mkv softlink
        files = os.listdir(path)
        files = [f for f in files if f.endswith(".mkv")]

        # Make sure we only have one file
        if len(files) != 1:
            print(colors.FAIL + "FAIL: " + colors.ENDC +
                    colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
                    "Detected " + str(len(files)) + " files in the directory. Exiting..")
            print()
            sys.exit(1)

        new_inote = path + inote_delim + "CREATE" + inote_delim + files[0]
        print(colors.CYAN + "INFO: " + colors.ENDC + 
                colors.OKBLUE +"<fix_args>" + colors.ENDC + " " + 
                "Returning new inote: " + 
                colors.WARNING + new_inote + colors.ENDC)

        print()
        return new_inote


def convert_inote_to_list(inote, conf):
    """
    This converts the inotifywait string returned in fix_args()
    to an array for the rest of the program to use.

    Note we need this method because if shows contain a "comma" in the name,
    str.split(',') will split on that too, in which case we need to reconnect
    the show names.

    Update v3: Delimiter has been changed to ||. All we need to do is split and return it.
    """

    # Get the delimiter
    inote_delim = conf['sys']['delimiter']

    print(colors.CYAN + "INFO: " + colors.ENDC +
            colors.OKBLUE + "<convert_note_to_ilist>" + colors.ENDC + " " +
            "Using delimiter: " + inote_delim)

    args = inote.split(inote_delim)

    print(colors.CYAN + "INFO: " + colors.ENDC +
            colors.OKBLUE + "<convert_note_to_ilist>" + colors.ENDC + " " +
            "Returning: " + 
            colors.WARNING + str(args) + colors.ENDC)

    print()
    return args


def create_clean_filename(filename, ext):
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
                
def convert(inote):

    # Clear the terminal and print out the received argument
    os.system('clear') if os.name != "nt" else os.system('cls')
    print(colors.CYAN + "INFO: " + colors.ENDC +
            colors.OKBLUE + "<convert>" + colors.ENDC + " " +  
            "Received argument: \"" + 
            colors.WARNING + inote + colors.ENDC + "\"", end="\n\n")

    conf = load_config()

    args = convert_inote_to_list(fix_args(inote, conf), conf)

if __name__ == "__main__":
    convert(sys.argv[1])

