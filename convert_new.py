## Author: J. R. Lu

import sys
import os

# Randint for file name generation, sleep for pause, quote for shell safety
from subprocess import call
from random import randint
from time import sleep
from shlex import quote

# For http notifications
import urllib.request
import json

# Don't do anything if the new file is a directory
if "ISDIR" in sys.argv[1]:
    print("New directory was made, doing nothing.")
    print("Input: " + str(sys.argv[1]))
    print()
    sys.exit(0)

#Constants

# Arg 1 is dir, Arg 2 is type, Arg 3 is filename
args = sys.argv[1].split(',') # Passed in args
mkv_fname = quote(args[2]) # show.mkv
mp4_fname = str(args[2][:-4]) + ".mp4" # show.mp4

# Get the absolute paths of the source files, for bash
# ..public_html/Public/Nyaa4/..

nyaa4 = str(args[0][0:60]) + str(args[0][61:65]) + "4" + str(args[0][65:])
nyaaKV = str(args[0][0:60]) + str(args[0][61:65]) + "KV" + str(args[0][65:])

# Full paths for the downloaded file and its mp4 equivalent
src_file = quote((args[0] + args[2]))
dest_file = quote((nyaa4 + mp4_fname))

# Fansub Prefixes
prefixes = list()
prefixes.append("[HorribleSubs] ")
prefixes.append("[meta] ")

# Create equivalent vars without fansub names
mkv_fname_clean = args[2]
for prefix in prefixes:
    mkv_fname_clean = mkv_fname_clean.replace(prefix, "", 1)

suffixes = list()
suffixes.append("[AoD] ")
for suffix in suffixes:
    if suffix in mkv_fname_clean:
        mkv_fname_clean = mkv_fname_clean.replace(suffix, "", 1)
        mkv_fname_clean = mkv_fname_clean[:-14] + ".mkv"

mp4_fname_clean = (str(mkv_fname_clean[:-4]) + ".mp4")

# Sanitize. DO THIS BEFORE YOU SANITIZE THE VARIABLES
src_dir_clean = nyaaKV
src_file_clean = quote((nyaaKV + mkv_fname_clean))
src_file_clean_notif = nyaaKV + mkv_fname_clean
dest_file_clean = quote((nyaa4 + mp4_fname_clean))
dest_file_clean_notif = nyaa4 + mp4_fname_clean


# The location of the temporary working directory
src_dir = args[0]
temp_dir = "/media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/.temp/"
temp_file = quote((temp_dir + mp4_fname))
temp_file_clean = quote((temp_dir + mp4_fname_clean))

# Sanitize for later use
# First we make a copy for notif later
mkv_fname_clean_notif = mkv_fname_clean
mp4_fname_clean_notif = mp4_fname_clean
mp4_fname = quote(mp4_fname)
mkv_fname_clean = quote(mkv_fname_clean)
mp4_fname_clean = quote(mp4_fname_clean)

# How long to wait for a file to download, replace with autotools
# Currently using autotools
wait_time = 180
copy_time = 15

# Return out of program if file is not a MKV file
#if not mp4_fname.endswith('.mkv'): sys.exit(0)

# FFMPEG usr executables
ffmpeg = "ffmpeg"
ffmpeg10 = "ffmpeg-10bit"

# Notifications
REQUEST_URL = "https://on.aeri.jp/post"
DIRHEAD = "/media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/.Nyaa/"
CAS = "Currently Airing Shows"
CASH = "Currently Airing Shows [Hardsub]" 


##############################################################
#                  CONVERSION BEGINS HERE                    #
##############################################################

print()
print()
print("Detected new file: " + mkv_fname)
print()
print("mkv_fname: " + mkv_fname)
print("mp4_fname: " + mp4_fname)
print("src_dir: " + src_dir)
print("nyaaKV: " + nyaaKV)
print("nyaa4: " + nyaa4)
print("mp4_fname_clean: " + mp4_fname_clean)
print("mkv_fname_clean: " + mkv_fname_clean)
print("src_file: " + src_file)
print("dest_file: " + dest_file)
print("src_file_clean: " + src_file_clean)
print("dest_file_clean: " + dest_file_clean)
print("temp_dir: " + temp_dir)
print("temp_file: " + temp_file)
print("temp_file_clean: " +  temp_file_clean)
print("mkv_fname_clean_notif: " + mkv_fname_clean_notif)
print("mp4_fname_clean_notif: " + mp4_fname_clean_notif)

print()
print()

sys.exit(0)

#########################################
#            HTTP REQUEST
#########################################
def get_show_name(show_path): # should be src_dir
    show = show_path.replace(DIRHEAD,'')
    show = (show[:-1])
    return show

def build_body(show_name, location, file_name, file_path, json_type):
    """
    show_name: The name of the show, should be from get_show_name
    location: Either CAS or CASH
    file_name: Name of file, should be either mp4_fname_clean_notif or mkv_fname_clean_notif
    file_path: Full path of the file, should be either src_file_clean or dest_file_clean
    json_type: 0 for mkv, 1 for mp4
    """
    body = dict()
    body['json-type'] = json_type # Identifier, do not change
    body['source'] = "Ananke" # Uploaded from Ananke
    body['show_name'] = show_name # See docs
    body['location'] = location
    body['file'] = file_name
    body['file_size'] = os.path.getsize(file_path) # Pass in bytes
    return body

def request(body):
    url = REQUEST_URL
    req = urllib.request.Request(url)
    # Endpoint requires json-encoded data, UTF-8 for weird characters
    req.add_header('Content-Type', 'application/json; charset=utf-8')
    jsdata = json.dumps(body)
    js8 = jsdata.encode('utf-8')
    req.add_header('Content-Length',len(js8))
    urllib.request.urlopen(req, js8)

############## FILE SLEEP ################

# Wait n seconds until the file is downloaded TODO
print("Waiting " + str(wait_time) + " seconds for file to complete downloading.")

# Print out waiting time
for i in range(wait_time, 0, -1):
    print("Seconds remaining: " + str(i) + "  \r",end="")
    sleep(1)
print()

############## FILE SLEEP #################
# Just call the script from the src_dir
os.chdir(src_dir)

# Create a clean copy at NyaaKV
os.system("mkdir -p " + quote(nyaaKV))
os.system("cp " + mkv_fname + " " + src_file_clean)

# Print out waiting time
print()
for i in range(copy_time, 0, -1):
    print("Copy seconds remaining: " + str(i) + "  \r",end="")
    sleep(1)
print()

############## UPLOAD MKV ################
# in the interest of mkv up first, we'll sync it before conversion
# Sync MKV and send a notification, first make sure rclone isn't running
print()
print("Syncing MKV to Triton Weeaboos...")
os.system("/media/9da3/rocalyte/private/scripts/clean/is_rclone.sh")
os.system("/media/9da3/rocalyte/private/scripts/airing/airing-weebs.sh")
req_mkv_show = get_show_name(src_dir)
bodyKV = build_body(req_mkv_show, CAS, mkv_fname_clean_notif, src_file_clean_notif, 0)
request(bodyKV)
print("Syncing completed.")
print()


############## CONVERSION #################

# Check if the file is 8 or 10 bit color
if "10bit" in src_file:
    print("A 10-bit file was detected. Switching to 10-bit encoder.")
    ffmpeg=ffmpeg10

# Execute the command
#os.system("mkdir -p " + quote(nyaa4))
# Shell script to call ffmpeg and move completed file to Nyaa4
os.chdir(src_dir_clean)
call('/media/9da3/rocalyte/private/scripts/ex_ffmpeg.sh %s %s %s %s %s %s'
        % (ffmpeg, src_file_clean, mkv_fname_clean, temp_file_clean, dest_file_clean, quote(nyaa4)), shell=True)

# Clear the temporary files and upload the newly converted file
sleep(10)

print()
print("Starting sync...")
# Make sure rclone isn't already running to prevent overlap
os.system("/media/9da3/rocalyte/private/scripts/clean/is_rclone.sh")
# Synchronize all the files to online

# Sync MKV and send a notification
#os.system("/media/9da3/rocalyte/private/scripts/airing/airing-weebs.sh")
#req_mkv_show = get_show_name(src_dir)
#bodyKV = build_body(req_mkv_show, CAS, mkv_fname_clean_notif, src_file_clean_notif, 0)
#request(bodyKV)

# Sync MP4 and send a notification
os.system("/media/9da3/rocalyte/private/scripts/mp4air/airing-weebs4.sh")
req_mp4_show = get_show_name(src_dir)
body4 = build_body(req_mp4_show, CASH, mp4_fname_clean_notif, dest_file_clean_notif, 1)
request(body4)

print("Synchronization completed.")
print()

# Now delete the new files
print("Clearing files and directories...")
os.chdir(temp_dir)

os.system("rm " + src_file_clean)
os.system("rm " + dest_file_clean)
# And clear their directores if necessary
os.system("rmdir " + quote(nyaaKV))
os.system("rmdir " + quote(nyaa4))

print("Cleared.")
print()
print("Completed job for: " + mp4_fname)
print()
