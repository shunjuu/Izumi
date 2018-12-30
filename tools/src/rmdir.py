import sys
import os

# This module is relatively simple, it's more or less a straightforward clear up

RMDIR = 'rclone rmdirs %s/"%s"/ --leave-root -v'

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
        print(RMDIR %(r[0], r[option]))

    return


