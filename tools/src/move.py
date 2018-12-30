import sys
import os

from lib import hisha2
import pprint as pp

FLAGS = "--delete-empty-src-dirs --progress --stats 1s --stats-one-line -v"
MOVE = 'rclone move %s/"%s"/"%s" %s/"%s"/"%s" %s'
# Example: rclone move toshokan:/Airing/SHOW_NAME toshokan:/Premiered/SHOW_NAME $FLAGS

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
    res = input("Is this okay? [y] or [n] or [m]: " )

    # If multi level, then we need to add intermittent directories
    if res == "y":
        pass

    elif res == "m":
        pre = input("Please input the existing path in between: ")

        if not pre.endswith("/"): pre += "/"
        new_folder_name = pre + new_folder_name

    else:
        new_folder_name = input("Please input a new folder name: ")

    for r in config.getList():
        rclone = r[0]
        src = r[1]
        dest = r[2]

        print(MOVE % (rclone, src, show, rclone, dest, new_folder_name, ""))
