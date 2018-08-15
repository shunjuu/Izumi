import os
import pprint as pp
import json
import shutil
import time

from shlex import quote
from threading import Thread

from flask import Flask, request
app = Flask(__name__)

def handle(r):
    print(r['episode'])

    # Copy the file into .hard/$EPISODE
    print("Downloading: " + r['episode'])
    rc = "rclone copy sanka-kan:Airing/" + quote(r['show']) + "/" + quote(r['episode']) + " " + "/home/izumi/izumi/.hard/" + " -v"
    #print(rc)
    os.system(rc)

    # Make the directory in .NyaaV2 if it doesn't exist
    print("Making destination directory if it does not exist...")
    di = "mkdir -p " + "/home/izumi/izumi/NyaaV2/" + quote(r['show'])
    #print(di)
    os.system(di)
    time.sleep(3) # sleep so the system doesn't overload

    # Hard link the file into the directory
    print("Hard linking the files...")
    ln = "ln " + "/home/izumi/izumi/.hard/" + quote(r['episode']) + " " + "/home/izumi/izumi/NyaaV2/" + quote(r['show']) + "/" + quote(r['episode']) 
    #print(ln)
    os.system(ln)

    # Delete the first link to the inode
    print("Deleting the original link to inode...")
    rmf = "rm " + "/home/izumi/izumi/.hard/" + quote(r['episode'])
    #print(rmf)
    os.system(rmf)

    print("Done")
    print()

@app.route("/", methods=['POST'])
def req():
#    handle(request.get_json()
#    handle(request.get_json())
    Thread(target=handle, args=(request.get_json(),)).start()
    return "Got it!", 418

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1400)
