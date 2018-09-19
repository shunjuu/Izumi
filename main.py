import sys, os, shutil
import pprint as pp
import re

from subprocess import call
from time import sleep
from shlex import quote

import requests
import json, yaml 

import anitopy 

# For finding show names intelligently
from lib import hisha

# Modules!
from src import filenames, paths
from src import cleanup

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


def get_runtype(input_type):
    """
    Takes the input_type string and gets the runtype from it.
    Returns "downloader" or "encoder".

    Method is mostly just to make sure that any similar-enough string 
    in the "type" is loaded properly.
    """

    lower_type = input_type.lower()
    rtype = str()
    if lower_type.startswith("d"):
        rtype = "downloader"
    elif lower_type.startswith("e"):
        rtype = "encoder"
    else:
        print()
        raise Exception("No proper config type found in config.yml!")
    
    print(colors.GREEN + "NOTICE: " + colors.ENDC +
            "Using mode \"" +
            colors.OKGREEN + rtype + colors.ENDC
            + "\""
            + ".")
    print()
    return rtype

def upload_mkv():
    """
    Call the script that uploads the matroska files.
    """

    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "Now uploading MKV files...")
    print() # Add one for before the script

    os.system("src/mkv.sh")

    print()
    return

def notify_mkv_upload(conf, mkv):
    """
    Sends a POST request that will issue notifications about the new mkv.
    We use Python to send the notification because curling in the bash shell
        is unreliable, as discovered from convert.sh.
    """

    print()
    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Now sending MKV upload notifications...")

    # Create the body
    body = dict()
    body['json-type'] = 1
    body['source'] = "Undefined"
    body['show_name'] = mkv['show_name']
    body['location'] = conf['notifications']['upload']['mkv']['name']
    body['file'] = mkv['new_filename']
    body['file_size'] = os.path.getsize(mkv['hardsubbed_file'])

    for url in conf['notifications']['upload']['mkv']['urls']:
        print(colors.LCYAN + "NOTIFICATION: " + colors.ENDC +
                "Sending notification to " +
                colors.OKBLUE + url + colors.ENDC + "... ", end="")
        try:
            r = requests.post(url, json=body)
            print(colors.OKGREEN + "Success" + colors.ENDC + ".")
        except:
            print(colors.FAIL + "Failed" + colors.ENDC + ".")

    print()
    return


def notify_mkv_encode(conf, mkv, izumi_type):
    """
    Attempts to send encoding information to the encoding servers in order, until one accepts.
    If none accept, then the downloader itself will fallback (or cancel) by setting izumi_type
    """

    # Create the request JSON
    body = dict()
    body['show'] = mkv['show_name']
    body['episode'] = mkv['new_filename']
    
    # Firstly, we attempt to do request a primary encoding. We need to mark it for failure
    # and fallback (if so), if so.
    PRIMARY_SUCCEED = False

    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Now sending requests to encoding server(s)...")

    for encoder in conf['sync']['mkv']['encoders']['primary']:

        try:
            print(colors.LCYAN + "NOTIFICATION: " + colors.ENDC +
                    "Sending primary encode request to " + 
                    colors.OKBLUE + encoder + colors.ENDC + "... ", end="")

            r = requests.post(encoder, json=body, timeout=5)
            # Continue onto the next one, as the current failed
            if r.status_code != conf['sync']['mkv']['encoders']['status_code']:
                raise Exception("Bad status code!")

            # Else if succeeded, we mark it as passed and exit out
            print(colors.OKGREEN + "Success" + colors.ENDC + ".")
            PRIMARY_SUCCEED = True
            break # Break out of the for loop and proceed to x265

        except:
            print(colors.FAIL + "Failed" + colors.ENDC + ".")
            continue

    print()

    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Now sending request to other encoding server(s)...")

    # Now, we try to notify extra encoders.
    # However, if it fails, we don't do anything and just continue
    for encoder in conf['sync']['mkv']['encoders']['other']:
        try:
            print(colors.LCYAN + "NOTIFICATION: " + colors.ENDC +
                    "Sending encode request to " + 
                    colors.OKBLUE + encoder + colors.ENDC + "... ", end="")
            r = requests.post(encoder, json=body, timeout=5)

            if r.status_code != conf['sync']['mkv']['encoders']['status_code']:
                # We just raise exception, since an error could be thrown while requesting
                raise Exception("Bad status code!")

            # Else if succeeded, just continue - we don't care
            print(colors.OKGREEN + "Success" + colors.ENDC + ".")
            continue

        except:
            print(colors.FAIL + "Failed" + colors.ENDC + ".")
            continue

    print()

    # If all the encoders did not respond, then the downloader needs to fallback (if set so)
    # and encode (if so)
    if not PRIMARY_SUCCEED:
        print(colors.WARNING + "INFO: " + colors.ENDC +
                "None of the primary encoders were successful.")
        # We only fallback if if specified to do so. Otherwise, just leave as is and return
        # to delete files.
        if conf['sync']['mkv']['encoders']['fallback']:
            print(colors.WARNING + "WARNING: " + colors.ENDC +
                    "Fallback mode is activated. Now switching to " + 
                    colors.WARNING + "encoder" + colors.ENDC + " " +
                    "mode.")
            print()
            return "encoder"

    print(colors.WARNING + "NOTICE: " + colors.ENDC + 
            "A primary encoder request was successful or Fallback is deactivated. Continuing as " +
            colors.WARNING + izumi_type + colors.ENDC + " " +
            "mode.")
    print()
    return izumi_type


def upload_mp4():
    """
    Call the script that uploads the matroska files.
    """

    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "Now uploading MP4 files...")
    print() # Add one for before the script

    os.system("src/mp4.sh")

    print()
    return


def notify_mp4_upload(conf, mp4):
    """
    Sends a POST request that will issue notifications about the new mp4.
    We use Python to send the notification because curling in the bash shell
        is unreliable, as discovered from convert.sh.
    """

    print()
    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Now sending MP4 upload notifications...")

    # Create the body
    body = dict()
    body['json-type'] = 2
    body['source'] = "Undefined"
    body['show_name'] = mp4['show_name']
    body['location'] = conf['notifications']['upload']['mp4']['name']
    body['file'] = mp4['new_filename']
    body['file_size'] = os.path.getsize(mp4['hardsubbed_file'])

    for url in conf['notifications']['upload']['mp4']['urls']:
        print(colors.LCYAN + "NOTIFICATION: " + colors.ENDC +
                "Sending notification to " +
                colors.OKBLUE + url + colors.ENDC + "... ", end="")
        try:
            r = requests.post(url, json=body)
            print(colors.OKGREEN + "Success" + colors.ENDC + ".")
        except:
            print(colors.FAIL + "Failed" + colors.ENDC + ".")

    print()
    return


def distribute_mp4(conf):
    """
    Makes a blank POST request to various destinations to notify them to distribute new MP4s
    """
    
    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Sending requests to distribute newly generate MP4 file(s)...")

    print(colors.WARNING + "NOTICE: " + colors.ENDC +
            "Now sending requests to "
            + colors.WARNING + "ALWAYS" + colors.ENDC +
            " destinations...")
    # First, post all of the "always" destinations
    for distributor in conf['sync']['mp4-distribution']['distributors']['always']:
        print(colors.LCYAN + "NOTIFICATION: " + colors.ENDC +
                "Sending request to " + 
                colors.OKBLUE + distributor + colors.ENDC +
                "... ",end="")
        try:
            r = requests.post(distributor, timeout=5)
            print(colors.OKGREEN + "Success." + colors.ENDC)
        except:
            print(colors.FAIL + "Failed." + colors.ENDC)

    # Second, try the sequential ones until one passes or all fail
    print(colors.WARNING + "NOTICE: " + colors.ENDC +
            "Now sending requests to "
            + colors.WARNING + "SEQUENTIAL" + colors.ENDC +
            " destinations...")
    for distributor in conf['sync']['mp4-distribution']['distributors']['sequential']:
        print(colors.LCYAN + "NOTIFICATION: " + colors.ENDC +
                "Sending request to " + 
                colors.OKBLUE + distributor + colors.ENDC +
                "... ",end="")
        try:
            r = requests.post(distributor, timeout=60)
            print(colors.OKGREEN + "Success" + colors.ENDC + ".")
            break
        except:
            print(colors.FAIL + "Failed" + colors.ENDC + ".")

    print()
    return


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
    izumi_type = get_runtype(conf['type'])

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
    filenames.get_source_filenames(mkv, mp4, args, True)

    # Get the show name, BE SURE TO RUN THIS BEFORE load_destination_folder_and_paths
    filenames.get_show_name(conf, mkv, mp4, args, True)

    # Use Anitopy to get the new, cleaned filenames
    filenames.generate_new_filenames(mkv, mp4, True)

    # Get the folders where a copy of the MKV and the new MP4 will be put.
    paths.load_destination_folder_and_paths(mkv, mp4, conf, args, True)
    paths.load_temp_folder_and_paths(mkv, mp4, conf, True)

    # We want to get the current working directory for reference
    # WORK_DIR/bin/ffmpeg{-10bit,}
    # Design note: The ffmpeg conversion script should not have to
    # figure out where it is - pass in the full path of the executable
    ffmpeg = dict()
    ffmpeg['dir_path'] = os.path.dirname(os.path.realpath(__file__)) + "/bin/"
    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "Application \"bin/\" directory: " + 
            colors.OKBLUE + "< ffmpeg['dir_path'] >" + colors.ENDC + " " +  
            colors.LMAGENTA + ffmpeg['dir_path'] + colors.ENDC)

    # ffmpeg executable
    ffmpeg['ffmpeg'] = ffmpeg['dir_path'] + "ffmpeg"
    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "ffmpeg executable path: " +
            colors.OKBLUE + "< ffmpeg['ffmpeg'] >" + colors.ENDC + " " +  
            colors.MAGENTA + ffmpeg['ffmpeg'] + colors.ENDC)

    ffmpeg['ffmpeg-10bit'] = ffmpeg['dir_path'] + "ffmpeg-10bit"
    print(colors.LCYAN + "INFO: " + colors.ENDC + 
            "ffmpeg-10bit executable path: " +
            colors.OKBLUE + "< ffmpeg['ffmpeg-10bit'] >" + colors.ENDC + " " +  
            colors.MAGENTA + ffmpeg['ffmpeg-10bit'] + colors.ENDC)

    print()


    # --------------------------------------------------------------------- #
    # String generation is complete, start to run transfer process
    # Note; izumi_type is the current type of downloader
    # --------------------------------------------------------------------- #
    
    """
    pp.pprint(mkv)
    print()
    pp.pprint(mp4)
    print()
    """

    # Step 1: We always want to copy the new file to a MKV: 
    # Note: Deprecation since we're using a temp file, we technically only want
    # to do this if we're in DOWNLOADER mode
    if izumi_type == "downloader":
        if not os.path.exists(mkv['new_hardsub_folder']):
            os.makedirs(mkv['new_hardsub_folder'])
        try:
            shutil.copy2(mkv['src_file_path'], mkv['hardsubbed_file'], follow_symlinks=True)
        except:
            print(colors.FAIL + "WARNING: " + colors.ENDC + 
                    "Shutil was unable to copy into the temp file.")
            print(colors.WARNING + "NOTE: " + colors.ENDC +
                    "This is probably just a duplicate autotools inotify notification.")
            sys.exit(2)

    # Step 2: Upload the file online, but only if mode is downloader
    # Step 2.5: If mode is downloader, only proceed from here if unsucessful call to proxies
    # Step 2.5: If mode is encoder, continue
    """
    if izumi_type == "downloader":
        upload_mkv()
        notify_mkv_upload(conf, mkv)
        izumi_type = notify_mkv_encode(conf, mkv, izumi_type)
        

    # Type check for encoder, as if encoder request succeeds, it will still continue 
    # to clear the files at the end
    if izumi_type == "encoder":
        # Step 3: Copy the file into a temp.mkv in temp for encoding
        shutil.copy2(mkv['src_file_path'], mkv['temp_file_path'], follow_symlinks=True)

        # Step 4: Execute ffmpeg script to encode videos
        # Make the directory the new folder will be in
        if not os.path.exists(mp4['new_hardsub_folder']):
            os.makedirs(mp4['new_hardsub_folder'])
        os.system("src/encode.sh %s %s"
                % (mkv['quoted_temp_file_path'], quote(mp4['hardsubbed_file'])))

        # Step 5: Upload the new MP4 file 
        upload_mp4()
        notify_mp4_upload(conf, mp4)

        # Step 5.1: If we're originally just an encoder, we need to post one of the heavy servers
        # for file transferring, or fallback to just uploading everything
        # Check conf, not izumi_type, to see if original runtype is encoder or downloader
        if get_runtype(conf['type']) == "encoder":
            distribute_mp4(conf)
    """
    # step 6: Clear out all the new files
    cleanup.clear_files(conf, mkv, mp4, True)

    print(colors.OKGREEN + "Completed job for: " + colors.ENDC + 
            mkv['src_filename'] + ".")
    print()
    sys.exit(0)

# Run convert if this file is invoked directly, which it will be
if __name__ == "__main__":
    burn(sys.argv[1])
