import sys
import os

import json

import pprint as pp

from lib.colors import Colors

FLAGS = "-v"
PURGE = 'rclone purge %s/"%s"/"%s" %s'
LIST = 'rclone lsjson -R %s/"%s"/"%s" 2>/dev/null'

c = Colors()


def _prompt(prompt):
    try:
        response = input(prompt)
    except:
        print("Exiting...")
        sys.exit(1)

    return response



def delete(config):

    loc = _prompt("Remove from Airing or Premiered? [a] or [p]: ")

    if loc.lower() == "a": 
        option = 1
    elif loc.lower() == "p": 
        option = 2
    else:
        print("Please enter a valid input!")
        return

    show = _prompt("Please enter the show to remove: ")

    for r in config.getList():

        print("Now working on %s%s%s (%s%s%s)" 
                % (Colors.WARNING, r[0], Colors.ENDC, 
                    Colors.OKBLUE, r[option], Colors.ENDC ))

        # Check if the path exists.
        res = os.popen(LIST % (r[0], r[option], show)).read()
        res = json.loads(res)

        # If the folder doesn't exist, skip it.
        if len(res) == 0:
            print("%sNOTICE%s: Path under %s%s/%s/%s%s does not exist, skipping..." 
                    % (Colors.WARNING, Colors.ENDC,
                        Colors.FAIL, r[0], r[option], show, Colors.ENDC))
            continue

        print("%sWARNING:%s Now deleting %s%s%s from %s..." % 
            (c.WARNING, c.ENDC, c.FAIL, show, c.ENDC, r[option]))

        os.system(PURGE % (r[0], r[option], show, FLAGS))
