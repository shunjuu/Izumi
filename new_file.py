"""
Module file that converts passed in files. 

Takes a inotifywait-style argument. CALL THIS FROM MAIN.

Author: aleytia@gitlab
"""

import sys
import os

# Calling for shell command, time for sleep, and quote for safety on spaces
from subprocess import call
from time import sleep
from shlex import quote

# To send HTTP POST requests for notifications
import urllib.request
import json

# Import raw ripper
import raw

# Import the anime name parser
import anitopy

import requests

# CONSTANTS

# The current version of ".Nyaa" folder we're using:
nyaa_fol = ".NyaaV2"

# Determine length to active, should only be for this module
wait_time = 180 # Deprecated
copy_time = 15 # Deprected

# ffmpeg user executables
ffmpeg = "ffmpeg" # Deprecated
ffmpeg1o = "ffmpeg-10bit" # Deprecated
THREADS=12

#-- HTTP POST constants
REQUEST_URL = "https://on.aeri.jp/post"
CAS = "Currently Airing Shows"
CASH = "Currently Airing Shows [Hardsub]"
TSUYU = "http://izumi.best.moe:1400"
WIZO = "http://sakura.wizo.sh:9696"

def parse_args(inotifywatch_str):

    print("Arg: " + inotifywatch_str)
    print()

    # Special case, we want to check for raws submodule 
    if "ReinForce" in inotifywatch_str:
        print("Reinforce RAW detected, switching modes...")
        raw.handle_raw(inotifywatch_str)
        sys.exit(0)

    args = inotifywatch_str.split(',')

    # This is a normal new file, we can just return the string as is
    if args[1] == "CREATE":
        print("Detected a regular file being made; returning argument string as-is.")

        try:
            if args[2].endswith(".meta"):
                print("Detected a meta file, ignoring...")
                sys.exit(0)
        except:
            print("There was an error when running the try block")
            pass

        print("Returning: " + inotifywatch_str, end="\n\n")
        return inotifywatch_str

    # This is a more common case: A new dir was made
    elif args[2] == 'ISDIR"':
        print("Detected new directory, processing...")
        path = args[0] + args[3] + "/"

        # Get all the files in the new dir, should only be the .mkv softlink
        files = os.listdir(path)
        files = [f for f in files if f.endswith(".mkv")]

        # Make sure we only have one file
        if len(files) != 1:
            print("The files list is not size 1; returning as an error...")
            print()
            sys.exit(1)

        new_watch_str = path + ",CREATE," + files[0]
        print("Returning: " + new_watch_str, end="\n\n")
        return new_watch_str


# Usually we'd check for ISDIR but we'll ignore it for this module

def get_dest_folder(og_abs_path, og_folder, dest_type):
    """
    Function to convert the abs_path (".../.Nyaa/...") to(".../Nyaa*/...")
    Params:

    - og_abs_path: "/root/var/www/Public/.Nyaa/{Show_name}/"
        - type(og_abs_path) == str

    - og_folder: ".Nyaa": The original (download) folder
        - type(og_folder) == str

    - dest_type: "NyaaKV" or "Nyaa4"
        - type(dest_type) == str

    This function is vital to allow the program to run in any folder
    """

    # Split the path by / into an array of strings
    original_path = og_abs_path.split('/')
    new_path = str()

    # Replace the one folder with the new folder
    for idx, folder in enumerate(original_path):
        if folder == og_folder:
            original_path[idx] = dest_type

    # Conjoin it back into a path.
    for folder in original_path:
        # Ignore empty entries
        if folder:
            new_path = new_path + "/" + folder

    # Add the last / since this is a directory
    new_path = new_path + "/"

    return new_path

def clean_filename(filename, ext):
    """
    Strip out fansub names from the filename
    params:
    - filename: The original, dirty filename
    - ext: The new extension to add
    """

    p = anitopy.parse(filename)
    new_file = p['anime_title']

    if 'anime_season' in p:
        new_file = new_file + " S" + p['anime_season']

    new_file = new_file + " - " + p['episode_number']

    # Release version
    if 'release_version' in p:
        new_file = new_file + "v" + p['release_version']

    # If uncensored, mark it
    if 'other' in p and 'uncensored' in p['other'].lower():
        new_file = new_file + " (Uncensored)"

    # Video res might not be included
    if 'video_resolution' in p:
        new_file = new_file + " [" + p['video_resolution'] + "]"

    new_file = new_file + ext
    return new_file


def get_DIRHEAD(src_dir, dl_folder):
    """
    Gets the path up to the .Nyaa folder, i.e.
    /media/9da3/rocalyte/.../Public/.Nyaa/"
    """
    original_path = src_dir.split('/')
    new_path = str()
    for folder in original_path:
        if folder:
            new_path = new_path + "/" + folder
        if folder == dl_folder:
            break
    new_path += "/"
    return new_path

def get_temp_dir(src_dir, dl_folder):
    """
    A modifer that gets the temporary working dir to generate MP4 files.
    params:
    - src_dir: The source directory of the new file.
        - It should be of the form: "...../Public/.Nyaa/{series name}..."
    """
    # Split the path by / into an array of strings
    original_path = src_dir.split('/')
    new_path = str()
    for folder in original_path:
        if folder == dl_folder:
            break
        if folder:
            new_path = new_path + "/" + folder

    new_path += "/"
    new_path = new_path + ".temp/"

    return new_path
    
### HTTP REQUESTS ###
def get_show_name(show_path, folder=nyaa_fol): # should be src_dir
    show = show_path.replace(get_DIRHEAD(show_path, folder),'')
    show = (show[:-1])
    return show

def build_body(location, file_name, file_path, json_type, show_path):
    """
    show_name: The name of the show, get it from get_show_name()
    location: Either CAS or CASH
    file name: name of the file, should be either mp4_fname_clean_notif or mkv_fname_clean_notif
    file_path: should be either src_file_clean or dest_file_clean
    json_type: 1 for CAS, 2 for CASH, 3 for PS, 4 for PSH
    """
    body = dict()
    body['json-type'] = json_type
    body['source'] = "Ananke 2"
    body['show_name'] = get_show_name(show_path)
    body['location'] = location
    body['file'] = file_name
    body['file_size'] = os.path.getsize(file_path) #use bytes
    return body

def request(location, file_name, file_path, json_type, show_path):
    url = REQUEST_URL
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsdata = json.dumps(build_body(location, file_name, file_path, json_type, show_path))
    js8 = jsdata.encode('utf-8')
    req.add_header('Content-Length', len(js8))
    try:
        urllib.request.urlopen(req, js8)
    except:
        pass

def sync_mkv(root_dir, mkv_fname_clean_notif, src_file_shlex, src_dir):
    print("Syncing MKV... (Using v2 background)")
    os.system(root_dir + "util/is_rclone.sh")
    os.system(root_dir + "sync/airing-mkv2.sh") 
    request("Airing", mkv_fname_clean_notif, src_file_shlex, 1, src_dir)
    print("Done syncing MKV files.")

def sync_mp4(root_dir, mp4_fname_clean_notif, dest_file_shlex, src_dir):
    print("Syncing MP4... (Using v2 background)")
    os.system(root_dir + "util/is_rclone.sh")
    os.system(root_dir + "sync/airing-mp42.sh")
    request("Airing [Hardsub]", mp4_fname_clean_notif, dest_file_shlex, 2, src_dir)
    print("Done syncing MP4 files.")

def rest(secs):
    """
    May not need this at all; used if the system needs to sleep
    """
    print("Resting " + str(secs) + " seconds...")
    for i in range(secs, -1, -1):
        print("Seconds remaining: " + str(i) + "...   \r",end="")
        sleep(1)
    print()

def purify_args(args):
    if len(args) < 3: return
    new_args = [None] * 2
    new_args[0] = args[0]
    new_args[1] = args[1]

    new_fname = args[2]

    for i in range(3, len(args)):
        new_fname = new_fname + "," + args[i]

    new_args.append(new_fname)

    return new_args

def cleanup(temp_dir, src_file, src_file_clean, nyaaKV_clean, src_dir_clean):
    os.chdir(temp_dir) # Switch into a directory that won't be deleted
    os.system("rm " + src_file) # src_file is the .NyaaV2 softlink/hardlink
    os.system("rm " + src_file_clean)
    os.system("rmdir " + nyaaKV_clean)
    os.system("rmdir " + src_dir_clean)


def tsuyu(mkv, show, og, temp_dir, src_file, src_file_clean, nyaaKV_clean, src_dir_clean):

    try:
        r = requests.post(TSUYU, json={"show": show, "episode": mkv})
        if r.status_code != 418:
            print("Status code isn't a teapot...")
            raise Exception('Bad status code!')

        print()
        print("Successfully called Tsuyu for encoding.")

        try:
            r = requests.post(WIZO, json={"show": show, "episode": mkv})
            if r.status_code != 418:
                print("Wizo failed to establish a connection.")
        except:
            print("Error occured with posting Wizo...")
            pass

        print("Succesfully called Wizo for libx265 encoding.")
        print("Completed download job for: " + og)
        print()
        cleanup(temp_dir, src_file, src_file_clean, nyaaKV_clean, src_dir_clean)
        sys.exit(0)

    except Exception as e:
        print("An error occured while attempting to post Tsuyu:")
        print(e)
        print("Continuing with standard...")

### THE ONLY METHOD YOU SHOULD CALL FROM MAIN ###
def convert(inotifywatch_str):
    """
    The main method that will call everything, generate variables, and convert.

    THIS METHOD IS ONLY FOR FILES, NOT DIRS.

    Params:

    - inotifywatch_str: An inotifywatch-style csv-style string.
    - Should be like: "/path/to/(series folder),CREATE,(new file)"
    """

    """
    CONSTANTS
    """

    print()
    print()
    args = parse_args(inotifywatch_str)

    args = args.split(',')
    args = purify_args(args)

    mkv_fname = args[2]
    mp4_fname = str(args[2][:-4]) + ".mp4"

    mkv_fname_clean = clean_filename(mkv_fname, ".mkv")
    mp4_fname_clean = clean_filename(mp4_fname, ".mp4")

    # Get these two before they're quoted
    mkv_fname_clean_notif = mkv_fname_clean
    mp4_fname_clean_notif = mp4_fname_clean

    nyaa4 = get_dest_folder(args[0], nyaa_fol, "Nyaa4")
    nyaaKV = get_dest_folder(args[0], nyaa_fol, "NyaaKV")

    nyaaKV_clean = quote(nyaaKV)
    nyaa4_clean = quote(nyaa4)

    src_dir = args[0]
    src_dir_clean = quote(src_dir)
    src_file = args[0] + args[2]
    dest_file = nyaa4 + mp4_fname

    src_file_clean = quote((nyaaKV + mkv_fname_clean))
    src_file_shlex = nyaaKV + mkv_fname_clean
    dest_file_clean = quote((nyaa4 + mp4_fname_clean))
    dest_file_shlex = nyaa4 + mp4_fname_clean

    temp_dir = get_temp_dir(args[0], nyaa_fol)
    temp_file = quote((temp_dir + mp4_fname))
    temp_file_clean = quote((temp_dir + mp4_fname_clean))

    # We now need to sanitize the rest of our inputs #
    mkv_fname = quote(mkv_fname)
    mp4_fname = quote(mp4_fname)
    mkv_fname_clean = quote(mkv_fname_clean)
    mp4_fname_clean = quote(mp4_fname_clean)
    src_file = quote(src_file)
    dest_file = quote(dest_file)
    temp_dir = quote(temp_dir)

    # Before we run everything, save ur current path
    root_dir = os.getcwd() + "/"

    # Print everything #
    # print("Current working directory: " + os.getcwd())
    # print()
    print("mkv_fname: " + mkv_fname)
    print("mkv_fname_clean: " + mkv_fname_clean)

    """
    print("mp4_fname: " + mp4_fname)
    print("mkv_fname_clean: " + mkv_fname_clean)
    print("mp4_fname_clean: " + mp4_fname_clean)
    print("mkv_fname_clean_notif: " + mkv_fname_clean_notif)
    print("mp4_fname_clean_notif: " + mp4_fname_clean_notif)
    print()
    print("src_dir: " + src_dir)
    print("src_dir_clean: " + src_dir_clean)
    print("nyaaKV: " + nyaaKV)
    print("nyaa4: " + nyaa4)
    print("nyaaKV_clean: " + nyaaKV_clean)
    print("Nyaa4_clean: " + nyaa4_clean)
    print()
    print("src_file: " + src_file)
    print("dest_file: " + dest_file)
    print("src_file_clean: " + src_file_clean)
    print("dest_file_clean: " + dest_file_clean)
    print("src_file_shlex: " + src_file_shlex)
    print()
    print("temp_dir: " + temp_dir)
    print("temp_file: " + temp_file)
    print("temp_file_clean: " + temp_file_clean)
    print()
    print("DIRHEAD: " + (get_DIRHEAD(src_dir, nyaa_fol)))
    print("show name: " + (get_show_name(src_dir, nyaa_fol)))
    print()
    """

    print()


    # Let us begin the conversion!
    try:
        os.chdir(src_dir)
    except:
        print("Unable to cd into the following directory. This invokation was likely one triggered by the previous delete.")
        print(src_dir)
        print()
        sys.exit(0)

    # Create a clean copy at NyaaKV
    os.system("mkdir -p " + nyaaKV_clean)
    os.system("cp -L " + mkv_fname + " " + src_file_clean)

    # Sync the MKV
    sync_mkv(root_dir, mkv_fname_clean_notif, src_file_shlex, src_dir)

    # Call Tsuyu for hardsubbing, if possible
    tsuyu(mkv_fname_clean_notif, get_show_name(src_dir, nyaa_fol), mkv_fname, temp_dir, src_file, src_file_clean, nyaaKV_clean, src_dir_clean)

    # Burn the subs
    os.chdir(nyaaKV)
    call(root_dir + "ex_ffmpeg.sh %s %s %s %s %s %s"
            % (src_file_clean, mkv_fname_clean, temp_file_clean, dest_file_clean, nyaa4_clean, str(THREADS)), shell=True)

    # Sync the MP4
    sync_mp4(root_dir, mp4_fname_clean_notif, dest_file_shlex, src_dir)

    # Cleanup

#    cleanup(temp_dir, src_file, src_file_clean, dest_file_clean, nyaaKV_clean, nyaa4_clean, src_dir_clean)

    os.chdir(temp_dir) # Switch into a directory that won't be deleted
    os.system("rm " + src_file) # src_file is the .NyaaV2 softlink/hardlink
    os.system("rm " + src_file_clean)
    os.system("rm " + dest_file_clean)
    os.system("rmdir " + nyaaKV_clean)
    os.system("rmdir " + nyaa4_clean)
    os.system("rmdir " + src_dir_clean)

    print("Cleared.",end="\n\n")
    print("Completed job for: " + mkv_fname,end="\n\n")

if __name__ == "__main__":
    convert(sys.argv[1])
    
