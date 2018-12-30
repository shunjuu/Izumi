import sys
import os

# This module is relatively simple, it's more or less a straightforward clear up

RMDIR = 'rclone rmdirs %s/"%s"/ --leave-root -v'

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def rmdir(config):

    try:
        folder = input("Remove Airing or Premiered folders? [a] or [p]: ")
    except:
        print("Exiting...")
        sys.exit(1)

    if folder.lower() == "a": option = 1
    elif folder.lower() == "p": option = 2
    else: 
        print("Please enter a valid input!")
        return

    for r in config.getList():
        print("%sNOTICE%s: Removing from %s%s%s..." 
                % (Colors.WARNING, Colors.ENDC, Colors.OKBLUE, r[0], Colors.ENDC), end=" ")
        sys.stdout.flush()
        os.system(RMDIR %(r[0], r[option]))
        print("Done")

    return


