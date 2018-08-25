import sys, os
import pprint as pp
import re

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
    GREEN = '\033[32m'
    WARNING = '\033[93m'
    LCYAN = '\033[0;96m'
    ORANGE = '\033[0;33m'
    MAGENTA = '\033[35m'
    LMAGENTA = '\033[95m'
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

        print(colors.LCYAN + "INFO: " + colors.ENDC + 
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

        print(colors.LCYAN + "INFO: " + colors.ENDC +
                colors.OKBLUE + "<fix_args>" + colors.ENDC + " " +
                "New file is not a meta file.")
        
        print(colors.LCYAN + "INFO: " + colors.ENDC + 
                colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
                "Returning unmodified inote: " + 
                "\"" + colors.WARNING + inote + colors.ENDC + "\"")

        print()
        return inote

    # A more common case, where the new directory is linked in.
    elif 'isdir' in inote.lower():
        print(colors.LCYAN + "INFO: " + colors.ENDC +
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
            print(colors.LCYAN + "INFO: " + colors.ENDC + 
                    colors.OKBLUE + "<fix_args>" + colors.ENDC + " " + 
                    "The runtype is Downloader. Proceeding to scan the directory for file(s).")
        
        # args[0] is the path up to the folder, args[3] is the name of the folder itself
        # folder name is args[3], not args[2], because extra comma is inserted between
        # CREATE,ISDIR, increasing the array length by 1
        # Update: args[2] instead of args[3] due to changes in delimiting to ||
        path = args[0] + args[2] + "/"
        print(colors.LCYAN + "INFO: " + colors.ENDC + 
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
        print(colors.LCYAN + "INFO: " + colors.ENDC + 
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

    print(colors.LCYAN + "INFO: " + colors.ENDC +
            colors.OKBLUE + "<convert_note_to_ilist>" + colors.ENDC + " " +
            "Using delimiter: " + colors.WARNING + inote_delim + colors.ENDC)

    args = inote.split(inote_delim)

    print(colors.LCYAN + "INFO: " + colors.ENDC +
            colors.OKBLUE + "<convert_note_to_ilist>" + colors.ENDC + " " +
            "Returning: " + 
            colors.WARNING + str(args) + colors.ENDC)

    print()
    return args


def get_source_filenames(mkv, mp4, args):
    """
    This method takes the MKV and MP4 name dicts and populates them with 
    source filenames.
    """

    # The original filename is guaranteed to be the second argument
    mkv['src_filename'] = args[2]

    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "MKV source filename: " + 
            colors.MAGENTA + mkv['src_filename'] + colors.ENDC)


    # The MP4 would be the same, just with an mp4 extension
    """
    mp4['src_filename'] = str(args[2][:-4] + ".mp4")

    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "MP4 source filename: " + 
            colors.MAGENTA + mp4['src_filename'] + colors.ENDC)
    """

    # Generate the full path of the source MKV file here
    mkv['src_file_path'] = args[0] + args[2]
    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "MKV source filepath: " + 
            colors.MAGENTA + mkv['src_file_path'] + colors.ENDC)

    print()
    return


def clean_filename(filename, ext):
    """
    Helper method.
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

def generate_new_filenames(mkv, mp4):
    """
    Populates the MKV and MP4 name dictionaries with new, "cleaned" names.
    Uses anitopy clean_filenames()
    """

    # Use clean_filename to generate the new clean filename
    mkv['new_filename'] = clean_filename(mkv['src_filename'], ".mkv")

    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "MKV new filename: " +
            colors.LMAGENTA + mkv['new_filename'] + colors.ENDC)

    mp4['new_filename'] = clean_filename(mkv['src_filename'], ".mp4")

    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "MP4 new filename: " +
            colors.LMAGENTA + mp4['new_filename'] + colors.ENDC)

    print()
    return


def load_hardsub_folder_and_paths(mkv, mp4, conf, args):
    """
    Pulls the folders in which the new MP4 file will be made.

    This method also loads the temp folder into MKV.
    Will throw an error if the temp folder contains a ' in it.

    !! DEPRECATED: MKV file is not copied twice. 
    !! Will use the temp folder for both.
    """

    # We need to run this safety method first, as the hardsub output file
    # relies on the show name existing
    if 'show_name' not in mkv or 'show_name' not in mp4:
        print(colors.WARNING + "NOTICE: " + colors.ENDC +
                colors.FAIL + "get_show_name()" + colors.ENDC + " " + 
                "not invoked before" + " " + 
                colors.FAIL + "load_hardsub_folder_and_paths()" + colors.ENDC + ", " +
                "executing " +
                colors.OKGREEN + "get_show_name()" + colors.ENDC + "...")
        get_show_name(mkv, mp4, args)

    # Load the folder for the MP4
    mp4['folder'] = conf['folders']['mp4']

    # Get the absolute path of the folder if it's not in abs
    mp4['folder'] = os.path.abspath(mp4['folder'])

    # If it doens't end with a "/", append it
    if not mp4['folder'].endswith("/"):
        mp4['folder'] += "/"


    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Hardsub base folder: " + 
            colors.MAGENTA + mp4['folder'] + colors.ENDC)

    # Generate the folder with the show name to place the new mp4 file in
    mp4['new_hardsub_folder'] = mp4['folder'] + mp4['show_name'] + "/"

    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Hardsub destination folder: " +
            colors.LMAGENTA + mp4['new_hardsub_folder'] + colors.ENDC)


    # Generate the output MP4 file string/path
    mp4['hardsubbed_file'] = mp4['folder'] + mp4['show_name'] + "/" + mp4['new_filename']

    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "Hardsub destination filepath: " +
            colors.LMAGENTA + mp4['hardsubbed_file'] + colors.ENDC)

    print()
    return


def load_temp_folder_and_paths(mkv, mp4, conf):
    """
    Helper method that will load and generate the temp folder path and the temp file.
    While mp4 is included, only the MKV dict is modified.
    """

    # Load the temp folder
    mkv['temp'] = conf['folders']['temp']

    # Get the absolute path of the folder if it's not in abs
    mkv['temp'] = os.path.abspath(mkv['temp'])

    # If it doens't end with a "/", append it
    if not mkv['temp'].endswith("/"):
        mkv['temp'] += "/"

    # We have to fail the system if ' appears in the temp folder, as it messes up
    # ffmpeg's parsing.
    if "'" in mkv['temp']:
        print(colors.FAIL + "FAIL: " + colors.ENDC +
                "Unexpected single quote was found in the temp folder path. The program will now exit.")
        sys.exit(1)

    # Print temp folder message
    """
    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "MKV temp. folder: " + 
            colors.MAGENTA + mkv['temp'] + colors.ENDC)
    """

    # For safety, we need to literal quote every folder in the temp path
    # Else ffmpeg may not properly load the folders
    temp_path = mkv['temp'].split("/")
    mkv['quoted_temp'] = str()
    for folder in temp_path:
        if folder:
            # Forcibly quote everything - shlex will not capture commas
            mkv['quoted_temp'] = mkv['quoted_temp'] + "/" + "'" + folder + "'"
    mkv['quoted_temp'] += "/"

    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "MKV quoted temp. folder: " +
            colors.LMAGENTA + mkv['quoted_temp'] + colors.ENDC)

    
    # The temporary file is guaranteed to be named "temp.mkv" for safety.
    # Get its path that can be used for -vf subtitles="path"
    mkv['temp_file_path'] = mkv['quoted_temp'] + "temp.mkv"

    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "Temp.mkv subtitles arg path: " + 
            colors.LMAGENTA + mkv['temp_file_path'] + colors.ENDC)

    print()
    return


def get_show_name(mkv, mp4, args):
    """
    Gets the show name from the args path and loads it into the two dictionaries.
    Uses Python re to match the words between the last two /../
    """

    # Pull the absolute path of up to and including the directory
    show_abs_path = args[0]

    show = re.match('.*\/(.*)\/', show_abs_path)
    show_name = show.group(1)

    mkv['show_name'] = show_name
    mp4['show_name'] = show_name

    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Show name: " + 
            colors.LMAGENTA + show_name + colors.ENDC)

    print()
    return()


def burn(inote):

    # Clear the terminal and print out the received argument
    os.system('clear') if os.name != "nt" else os.system('cls')
    print(colors.LCYAN + "INFO: " + colors.ENDC +
            colors.OKBLUE + "<convert>" + colors.ENDC + " " +  
            "Received argument: \"" + 
            colors.WARNING + inote + colors.ENDC + "\"", end="\n\n")

    # Load the config file, must be named "config.yml"
    conf = load_config()

    # Detremine what type of Izumi we're running
    izumi_type = conf['type']
    print(colors.GREEN + "NOTICE: " + colors.ENDC +
            "Using mode \"" +
            colors.OKGREEN + izumi_type + colors.ENDC
            + "\""
            + ".")
    print()

    # Load a fixed inote string into an array
    args = convert_inote_to_list(fix_args(inote, conf), conf)


    # -- GENERATE THE FILENAME STRINGS -- #
    print(colors.GREEN + "NOTICE: " + colors.ENDC + 
            "Now generating new filenames and filepaths..." + colors.ENDC,
            end="\n\n")

    # Create two dicts: One for MKV names and one for MP4 names
    mkv = dict()
    mp4 = dict()

    # Get the base name of the MKV file, and its MP4 equivalent
    get_source_filenames(mkv, mp4, args)

    # Get the show name, BE SURE TO RUN THIS BEFORE load_hardsub_folder_and_paths
    get_show_name(mkv, mp4, args)

    # Use Anitopy to get the new, cleaned filenames
    generate_new_filenames(mkv, mp4)

    # Get the folders where a copy of the MKV and the new MP4 will be put.
    load_hardsub_folder_and_paths(mkv, mp4, conf, args)
    load_temp_folder_and_paths(mkv, mp4, conf)

    # We want to get the current working directory for reference
    # WORK_DIR/bin/ffmpeg{-10bit,}
    # Design note: The ffmpeg conversion script should not have to
    # figure out where it is - pass in the full path of the executable
    ffmpeg = dict()
    ffmpeg['dir_path'] = os.path.dirname(os.path.realpath(__file__)) + "/bin/"
    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "Application \"bin/\" directory: " + 
            colors.LMAGENTA + ffmpeg['dir_path'] + colors.ENDC)

    # Add the other ffmpeg executables here
    ffmpeg['ffmpeg'] = ffmpeg['dir_path'] + "ffmpeg"
    ffmpeg['ffmpeg-10bit'] = ffmpeg['dir_path'] + "ffmpeg-10bit"
    print()


    # --------------------------------------------------------------------- #
    # String generation is complete, start to run transfer process
    # --------------------------------------------------------------------- #
    
     



# Run convert if this file is invoked directly, which it will be
if __name__ == "__main__":
    burn(sys.argv[1])
