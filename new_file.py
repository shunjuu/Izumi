"""
Module file that converts passed in files. 
!! THIS IS NOT FOR CREATE,ISDIR !!

Takes a inotifywait-style argument. CALL THIS FROM MAIN.

Author: reverie-lu@github
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


# CONSTANTS
# Determine length to active, should only be for this module
wait_time = 180
copy_time = 15

# ffmpeg user executables
ffmpeg = "ffmpeg"
ffmpeg1o = "ffmpeg-10bit"

#-- HTTP POST constants
REQUEST_URL = "https://on.aeri.jp/post"
CAS = "Currently Airing Shows"
CASH = "Currently Airing Shows [Hardsub]"


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

    # Strip fansub names that only have a prefix
    prefixes_only = list()
    prefixes_only.append("[HorribleSubs] ")
    prefixes_only.append("[meta] ")

    # Strip fansub groups that have both a prefix and a suffix
    pre_and_suff14 = list()
    pre_and_suff14.append("[AoD] ")

    newname = filename
    for prefix in prefixes_only:
        newname = newname.replace(prefix, "", 1)

    for ix in pre_and_suff14:
        if ix in newname:
            newname = newname.replace(ix, "", 1)
            newname = newname[:-14] + ext

    return newname

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

def get_temp_dir(src_dir):
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
        if folder == ".Nyaa":
            break
        if folder:
            new_path = new_path + "/" + folder

    new_path += "/"
    new_path = new_path + ".temp/"

    return new_path
    
### HTTP REQUESTS ###
def get_show_name(show_path): # should be src_dir
    show = show_path.replace(get_DIRHEAD(show_path, ".Nyaa"),'')
    show = (show[:-1])
    return show

def build_body(location, file_name, file_path, json_type, show_path):
    """
    show_name: The name of the show, get it from get_show_name()
    location: Either CAS or CASH
    file name: name of the file, should be either mp4_fname_clean_notif or mkv_fname_clean_notif
    file_path: should be either src_file_clean or dest_file_clean
    json_type: 0 for CAS, 1 for CASH, 2 for PS, 3 for PSH
    """
    body = dict()
    body['json-type'] = json_type
    body['source'] = "Ananke"
    body['show_name'] = get_show_name(show_path)
    body['location'] = location
    body['file'] = file_name
    body['file_size'] = os.path.getsize(file_path) #use bytes
    return body

def request(body, location, file_name, file_path, json_type, show_path):
    url = REQUEST_URL
    req - urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsdata = json.dumps(build_body(location, file_name, file_path, json_type, show_path))
    js8 = jsdata.encode('utf-8')
    req.add_header('Content-Length', len(js8))
    urllib.request.urlopen(req, js8)


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

    args = inotifywatch_str.split(',')

    mkv_fname = args[2]
    mp4_fname = str(args[2][:-4]) + ".mp4"

    mkv_fname_clean = clean_filename(mkv_fname, ".mkv")
    mp4_fname_clean = clean_filename(mp4_fname, ".mp4")

    # Get these two before they're quoted
    mkv_fname_clean_notif = mkv_fname_clean
    mp4_fname_clean_notif = mp4_fname_clean

    nyaa4 = get_dest_folder(args[0], ".Nyaa", "Nyaa4")
    nyaaKV = get_dest_folder(args[0], ".Nyaa", "NyaaKV")

    nyaaKV_clean = quote(nyaaKV)
    nyaa4_clean = quote(nyaa4)

    src_dir = args[0]
    src_file = args[0] + args[2]
    dest_file = nyaa4 + mp4_fname

    src_file_clean = quote((nyaaKV + mkv_fname_clean))
    dest_file_clean = quote((nyaa4 + mp4_fname_clean))

    temp_dir = get_temp_dir(args[0])
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

    # Print everything #
    print("mkv_fname: " + mkv_fname)
    print("mp4_fname: " + mp4_fname)
    print("mkv_fname_clean: " + mkv_fname_clean)
    print("mp4_fname_clean: " + mp4_fname_clean)
    print("mkv_fname_clean_notif: " + mkv_fname_clean_notif)
    print("mp4_fname_clean_notif: " + mp4_fname_clean_notif)
    print()
    print("src_dir: " + src_dir)
    print("nyaaKV: " + nyaaKV)
    print("nyaa4: " + nyaa4)
    print("nyaaKV_clean: " + nyaaKV_clean)
    print("Nyaa4_clean: " + nyaa4_clean)
    print()
    print("src_file: " + src_file)
    print("dest_file: " + dest_file)
    print("src_file_clean: " + src_file_clean)
    print("dest_file_clean: " + dest_file_clean)
    print()
    print("temp_dir: " + temp_dir)
    print("temp_file: " + temp_file)
    print("temp_file_clean: " + temp_file_clean)
    print("DIRHEAD: " + (get_DIRHEAD(src_dir, ".Nyaa")))
    print("show name: " + (get_show_name(src_dir)))

    # Cleanup
  # os.system("mkdir -p " + temp_dir)
   # sleep(10)
  # os.system("rmdir " + temp_dir)

if __name__ == "__main__":
    convert(sys.argv[1])
    
