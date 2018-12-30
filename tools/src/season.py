import os
import sys

import json

LIST = 'rclone lsjson -R %s/"%s"/"%s"'

MKDIR = 'rclone mkdir %s/"%s"/"%s"'
MOVE1 = 'rclone move %s/"%s"/"%s" %s/"%s"/"%s"'
MOVE2 = 'rclone move %s/"%s"/"%s" %s/"%s"/"%s" --delete-empty-src-dirs'

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def season(config):
    """
    This moves files in a directory into a seasonal directory in the same path:
    Grand Blue/{files} --> Grand Blue/Season 1/{files}

    Commands: 
        1. Move all {files} to the same path, but with parent dir path added with - temp
        2. Move all {files} from temp to path/{Season}, and remove the temp path.
    """

    # This command only works with Premiered shows.
    try:
        path = input("Please enter the path of the show, with Premiered as root: ")
        new_season = input("Please input the season folder name: ")
    except:
        print("Exiting...")
        sys.exit(1)

    # For each path, update it
    for r in config.getList(): 

        print("Now working on %s%s%s (%s%s%s)" 
                % (Colors.WARNING, r[0], Colors.ENDC, 
                    Colors.OKBLUE, r[2], Colors.ENDC ))

        # Check if the path exists.
        res = os.popen(LIST % (r[0], r[2], path)).read()
        res = json.loads(res)

        # If the folder doesn't exist, skip it.
        if len(res) == 0:
            print("%sNOTICE%s: Path under %s%s/%s/%s%s does not exist, skipping..." 
                    % (Colors.WARNING, Colors.ENDC,
                        Colors.FAIL, r[0], r[2], path, Colors.ENDC))

        # Move the files first to a temporary directory, append " - temp" to parent path
        if path.endswith("/"): 
            path = path[:-1] # Splice the last "/" out
        temp_path = path + " - temp"

        # Make the temp dir and move
        print("%sNOTICE%s: Making temporary directory: %s%s/%s/%s%s..." 
                % (Colors.WARNING, Colors.ENDC, 
                    Colors.FAIL, r[0], r[2], temp_path, Colors.ENDC), end=" ")
        sys.stdout.flush()
        os.system(MKDIR % (r[0], r[2], temp_path))
        print("Done")

        print("%sNOTICE:%sMoving files to temporary directory..." 
                % (Colors.WARNING, Colors.ENDC), end=" ")
        sys.stdout.flush()
        os.system(MOVE1 % (r[0], r[2], path, r[0], r[2], temp_path))
        print("Done")

        new_path = path + "/" + new_season
        print("%sNOTICE%s: Moving files to %s%s/%s/%s%s..." 
                % (Colors.WARNING, Colors.ENDC, Colors.FAIL, r[0], r[2], new_path, Colors.ENDC),
                end=" ")
        sys.stdout.flush()
        os.system(MOVE2 % (r[0], r[2], temp_path, r[0], r[2], new_path))
        print("Done")


