import sys, os
import pprint as pp
import json, yaml
import shutil
import time

from shlex import quote

# We need to thread handling to immediately give a response
from threading import Thread

from flask import Flask, request

# For somem printing statements
from src import initialize
from src import prints_server as prints

c = prints.Colors()
p = prints.Printouts()

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


# Load the configuration file
#def load_config():
    """
    Loads the config.yml file into ad ict
    """
 #   with open("config.yml", 'r') as conf:
  #      try:
   #         return yaml.load(conf)
    #    except:
     #       print("An exception occured while loading the config.")
      #      sys.exit(-1)

# set the flask name and load the config
app = Flask(__name__)

def do_encode(req):

    # Double read, so it loads the new config everytime
    conf = initialize.load_config()
    verbose = conf['sys']['verbose']

    # I prefer a quick sleep so the response code always prints first
    time.sleep(1)

    """
    print()
    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Received an encoding request for: " + 
            colors.WARNING + req['episode'] + colors.ENDC + ".")
    """

    p.p_encode_start(req['episode'])

    # The new path will simply be the watch folder + the new show folder,
    # as the show folder is guaranteed to be correct

    # First, get the watch folder and add a "/" to the end if not there
    watch_folder = conf['folders']['watch']
    watch_folder = os.path.abspath(watch_folder)
    watch_folder = watch_folder if watch_folder.endswith("/") else (watch_folder + "/")

    if verbose:
        p.p_encode_watch_detect(watch_folder)
    """
    print(colors.LCYAN + "INFO: " + colors.ENDC +
            "Detected watch folder located at: " + 
            colors.WARNING + watch_folder + colors.ENDC + ".")
    """
    
    # Note: We always just create the folder in this case, because Hisha may not
    # return the custom specified folders
    new_show_folder = watch_folder + req['show']
    if not os.path.exists(new_show_folder):
        if verbose:
            p.p_encode_show_folder_create(new_show_folder)
        """
        print(colors.LCYAN + "INFO: " + colors.ENDC +
                "Created show folder at " + 
                colors.WARNING + new_show_folder + colors.ENDC + ".")
        """
        os.makedirs(new_show_folder)
    #print()

    # Now download the new show into the hard folder

    # Get the source folder and add "/" if needed, and quote for spaces when applicable
    rclone_source = conf['sync']['mp4-distribution']['encoder']['source']
    rclone_source = rclone_source if rclone_source.endswith("/") else (rclone_source + "/")
    rclone_source = rclone_source + quote(req['show']) + "/" + quote(req['episode'])
    if verbose:
        p.p_encode_rclone_source(rclone_source)
    #print(colors.WARNING + "NOTICE: " + colors.ENDC +
    #        "Sourcing from: \"" + colors.WARNING + rclone_source + colors.ENDC + "\".")

    # Get the destination folder, and quote where necessary
    dest_folder_unclean = conf['folders']['hard'].split("/")
    rclone_dest = str()
    for folder in dest_folder_unclean:
        if folder:
            rclone_dest = rclone_dest + "/" + quote(folder)
    if verbose:
        p.p_encode_rclone_saving_dest(rclone_dest)
    """
    print(colors.WARNING + "NOTICE: " + colors.ENDC + 
            "Saving to:  + colors.WARNING + rclone_dest + colors.ENDC + ".")
    print()
    """

    # Download the file
    if verbose:
        p_encode_download_new_ep()
    #print(colors.WARNING + "NOTICE: " + colors.ENDC + 
    #       "Downloading new episode...")
    #os.system("rclone copy " + rclone_source + " " + rclone_dest + " -v")

    # Hard link the file into the new directory
    rclone_dest_file = rclone_dest if rclone_dest.endswith("/") else (rclone_dest + "/")
    rclone_dest_file += req['episode']
    new_episode_in_watch = new_show_folder if new_show_folder.endswith("/") else (new_show_folder + "/")
    new_episode_in_watch += req['episode']
    os.link(rclone_dest_file, new_episode_in_watch)

    # Once it's linked, delete the file in hard/
    os.remove(rclone_dest_file)

    # Print some kind of done statement
    p.p_encode_completed(req['episode'])

def do_distribute():
    time.sleep(1)
    os.system("src/distribute.sh")
    return

@app.route("/encode", methods=['POST'])
def encode():
    Thread(target=do_encode, args=(request.get_json(),)).start()
    return "Received encode request", conf['sync']['mkv']['encoders']['status_code']

@app.route("/distribute", methods=['POST'])
def distribute():
    Thread(target=do_distribute).start()
    return "Received distribution request", conf['sync']['mkv']['encoders']['status_code']

if __name__ == "__main__":
    conf = initialize.load_config()
    app.run(host='0.0.0.0', port=conf['sync']['mp4-distribution']['encoder']['port'])
