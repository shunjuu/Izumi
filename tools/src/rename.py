import os
import sys
import json
import pprint as pp

import anitopy

LIST = 'rclone lsjson -R %s/"%s"/"%s" 2>/dev/null'
#       rclone lsjson -R kan:/"Premiered"/"SHOW_NAME"

RENAME_SINGLE ='rclone moveto %s/"%s"/"%s" %s/"%s"/"%s"'
# actually the same as RENAME_MASS, but we'll separate in case future split

RENAME_MASS ='rclone moveto %s/"%s"/"%s"/"%s" %s/"%s"/"%s"/"%s"'
#       rclone moveto kan:/"Airing"/"Goblin Slayer"/"BAD_NAME"
#                       kan:/"Airing"/"Goblin Slayer"/"GOOD_NAME"


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def rename_single(config):
    """
    This is just designed to rename a single folder or file (usually folder) across the entire system
    """
    # Determine if from Airing or Premiered
    try:
        root = input("Rename from the Airing or Premiered folder? [a] or [p]: ")
    except:
        print("Exiting...")
        sys.exit(1)

    if root.lower() == "a": option = 1
    elif root.lower() == "p": option = 2
    else:
        print("Please enter a valid input!")
        return

    # Get the name of the root folder with files to rename
    # This must be the full path and will not use Hisha
    try:
        folder = input("Enter the folder path: ")
        new_name = input("Enter the new name for the folder (Do not enter parents or slashes): ")
    except:
        print("Exiting....")
        sys.exit(1)

    new_folder = folder.split("/")[:-1]
    new_folder.append(new_name)
    new_folder = "/".join(new_folder)

    for r in config.getList():
        # Check if the path exists. If so, then let's rename it
        res = os.popen(LIST % (r[0], r[option], folder)).read()
        res = json.loads(res)

        # If the folder doesn't have files or isn't found, skip it
        if len(res) == 0:
            print("%sNOTICE%s: Path under %s%s%s is empty, skipping..." 
                    %(Colors.WARNING, Colors.ENDC, Colors.OKBLUE, r[0], Colors.ENDC))
            continue

        print("\nNow checking %s%s%s (%s%s%s):"
                % (Colors.WARNING, r[0], Colors.ENDC,
                    Colors.OKBLUE, r[option], Colors.ENDC))

        os.system(RENAME_SINGLE % (r[0], r[option], folder, r[0], r[option], new_folder))



def _rename_mass(filename):
    """
    
    Usage for mass renaming files within a folder.

    Strip out fansub names from the filename
    Params: 
    - filename: The original, dirty filename

    Does not change extension, returns new filename
    """

    p = anitopy.parse(filename)
    new_file = p['anime_title']

    # Season
    if 'anime_season' in p:
        new_file += " S" + p['anime_season']

    # Episode number, NCED
    if 'episode_number' in p:
        new_file += " - " + p['episode_number']

    # Release version
    if 'release_version' in p:
        new_file += "v" + p['release_version']

    # If uncensored, mark it
    if 'other' in p and 'uncensored' in p['other'].lower():
        new_file += " (Uncensored)"

    # Video res might not be included 
    if 'video_resolution' in p:
        if "1920x1080" in p['video_resolution']:
            p['video_resolution'] = "1080p"

        p['video_resolution'] = p['video_resolution'].replace("P", "p")

        if 'p' not in p['video_resolution'].lower():
            p['video_resolution'] += "p"

        new_file += " [" + p['video_resolution'] + "]"

    new_file += "." + p['file_extension']
    return new_file

#if __name__ == "__main__":
    #print(_rename_mass(sys.argv[1]))

def rename_mass(config):
    """

    This method is for mass-renaming episodes inside a folder.

    1. Ask user if they want to rename files in the Airing or Premiered folders
        - This may apply to folders that don't exist - lsjson will return an empty list
    2. Ask user which show they want to remove
    3. For each episode found, remove 'em!
    """

    # Determine if from Airing or Premiered
    try:
        root = input("Rename from the Airing or Premiered folder? [a] or [p]: ")
    except:
        print("Exiting...")
        sys.exit(1)

    if root.lower() == "a": option = 1
    elif root.lower() == "p": option = 2
    else:
        print("Please enter a valid input!")
        return

    # Get the name of the root folder with files to rename
    # This must be the full path and will not use Hisha
    try:
        folder = input("Enter the root folder name: ")
    except:
        print("Exiting....")
        sys.exit(1)

    # Do the operation for every folder
    for r in config.getList():

        res = os.popen(LIST % (r[0], r[option], folder)).read()
        res = json.loads(res)

        # If the folder doesn't have files or isn't found, skip it
        if len(res) == 0:
            print("%sNOTICE%s: Path under %s%s%s is empty, skipping..." 
                    %(Colors.WARNING, Colors.ENDC, Colors.OKBLUE, r[0], Colors.ENDC))
            continue

        print("\nNow checking %s%s%s (%s%s%s):"
                % (Colors.WARNING, r[0], Colors.ENDC,
                    Colors.OKBLUE, r[option], Colors.ENDC))

        # Process each episode
        for ep in res:

            # Skip directories, we only rename eipsodes
            if ep['IsDir']: continue

            # Print what episode currently being processed
            print("%sFound: %s%s%s..."%(Colors.HEADER, Colors.OKGREEN, ep['Name'], Colors.ENDC), end=" ")

            # Get new name and check if it matches...
            new_name = _rename_mass(ep['Name'])
            if new_name == ep['Name']:
                print("skipping.")
                continue

            # Reaching this point means a file needs to be renamed
            new_path = ep['Path'].replace(ep['Name'], new_name)
            print("Renaming to: %s%s%s..." % (Colors.FAIL, new_name, Colors.ENDC), end=" ")
            # Force flush the buffer
            sys.stdout.flush()

            # Rename
            os.system(RENAME_MASS % (r[0], r[option], folder, ep['Path'], 
                                r[0], r[option], folder, new_path))
            print("done.")

