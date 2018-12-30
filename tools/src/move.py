import sys
import os

from lib import hisha2
import pprint as pp

FLAGS = "--delete-empty-src-dirs --progress --stats 1s --stats-one-line -v"
MOVE = 'rclone move %s/"%s"/"%s" %s/"%s"/"%s" %s'
# Example: rclone move toshokan:/Airing/SHOW_NAME toshokan:/Premiered/SHOW_NAME $FLAGS

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def move(config):

    show = input("Please enter the show name: ")
    try:
        native = hisha2.hisha(show, "native")
    except:
        pass

    try:
        new_folder_name = show + " ~ " + native
    except:
        new_folder_name = show

    print()
    print("New folder name: " + new_folder_name)
    res = input("Is this okay? [y] or [n] or [i]: " )

    # If multi level, then we need to add intermittent directories
    if res == "y":
        pass

    elif res == "i":
        pre = input("Please input the existing path in between: ")

        if not pre.endswith("/"): pre += "/"
        new_folder_name = pre + new_folder_name

    else:
        new_folder_name = input("Please input a new folder name: ")

    for r in config.getList():
        rclone = r[0]
        src = r[1]
        dest = r[2]

        print("%sNOTICE:%s Moving files in %s%s%s..." 
                % (Colors.WARNING, Colors.ENDC, Colors.OKBLUE, r[0], Colors.ENDC), end=" ")
        sys.stdout.flush()
        os.system(MOVE % (rclone, src, show, rclone, dest, new_folder_name, ""))
        print("Done")
