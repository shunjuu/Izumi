
from collections import OrderedDict
from os import listdir, walk
from os.path import exists, getsize, isdir, isfile, join
from pprint import pprint
from queue import Queue
from signal import signal, SIGINT
from sys import exit
from time import sleep
from typing import List, Tuple

# Quick function handler for cleanly exiting
def sigint_handler(sig, frame):
    print("\rKill command detected, exiting...")
    exit()
signal(SIGINT, sigint_handler)

class Toudai:

    class TrackingFile:
        """
        Internal class to store information about files we are tracking
        """
        def __init__(self, file):
            self.file: Tuple[str, str, str] = file # Holds the tuple tracked in Watch()
            self.filesize: int = getsize(self.file[0]) # Byte size of the file Toudai is tracking
            self.added: bool = False # A boolean to track if this TF was added into the Queue
            # self.added basically marks whether or not a file is ready to be removed from global_tracker 

    @staticmethod
    def get_curr_files(path: str) -> List[Tuple[str, str, str]]:
        """
        Gets all the files in the current watching path, returns as a list of tuples
        where:
        ( new_file_abs_path, root_folder, file_name )
        """
        curr_files: List[Tuple[str, str, str]] = list()
        for root, _, files in walk(path):
            for file in files:
                curr_files.append((join(root, file), root, file))
        return curr_files

    @staticmethod
    def idx_curr_files(fullpath: str, curr_files: List[Tuple[str, str, str]]) -> int:
        """
        Returns the index of whether or not a given fullpath is in the current files list
        If not, returns -1
        """
        for i in range(0, len(curr_files)):
            if curr_files[i][0] == fullpath:
                return i
        return -1

    @staticmethod
    def watch(path: str, queue: Queue, interval: int = 5) -> None:
        """
        Watches a given path and tracks all the files in that path directory.
        Checks every interval, and once a file has unchanged, append the event 
        into the queue.

        Params:
            path: Path to a directory that Toudai will watch
            queue: A global job queue for Izumi
            interval: Time, in seconds, to wait
        """
        if not exists(path) or not isdir(path):
            print("Invalid path passed in")
            # TODO: Log out some errors and exit
        
        global_tracker = OrderedDict()
        while True:
            # Get an updated list of all of our current working files
            #files = [f for f in listdir(path) if isfile(join(path, f))]
            curr_files = Toudai.get_curr_files(path)

            for fullpath, tf in global_tracker.items():
                # Ignore files we already processed
                if tf.added:
                    continue

                curr_file_idx = Toudai.idx_curr_files(fullpath, curr_files)
                if curr_file_idx >= 0:
                    print("{} exists, process it now".format(fullpath))
                    # Do a size comparison - unchanged sizes are done, changed sizes need to wait again

                    global_filesize = tf.filesize
                    curr_filesize = getsize(fullpath) # It's the same path as the curr path

                    print("two sizes: {} bytes vs {} bytes".format(global_filesize, curr_filesize))

                    if global_filesize != curr_filesize:
                        print("Found a filesize change for {}".format(fullpath))
                        global_tracker[fullpath].filesize = curr_filesize
                        continue
                    else:
                        print("No size differences were found, adding to queue")
                        global_tracker[fullpath].added = True

                else:
                    global_tracker.pop(fullpath)
                    print("Deleted {} from the global tracker".format(fullpath))

            print()


            # Add new files in curr_files to the global_tracker
            for file in curr_files:
                if file[0] not in global_tracker:
                    global_tracker[file[0]] = Toudai.TrackingFile(file)
                    print("added {} to global tracker".format(file[0]))
            

            print("---------------------------------------")
            # Finally, sleep
            sleep(interval)

if __name__ == "__main__":
    global_queue = Queue()

    Toudai.watch("/Users/adieuri/Desktop/Watch", global_queue, 5)
