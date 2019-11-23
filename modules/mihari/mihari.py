from os import walk
from os.path import join
from queue import Queue
from signal import signal, SIGINT
from sys import exit
from time import sleep
from typing import List, Tuple

def sigint_handler(sig, frame):
    print("\rKill command detected, exiting...")
    exit()

class Mihari:

    class MihariEvent:
        """
        Event that is added into the Queue for processing
        """
        def __init__(self, fullpath: str, root: str, name: str, watch: str):
            self._fullpath: str = fullpath # The full path of the new file that Toudai was watching
            self._root: str = root # Root path of the new file
            self._name: str = name # Name of the new file, not including the path
            self._watch: str = watch # Path that Toudai is watching

        @property
        def fullpath(self) -> str:
            return self._fullpath
        
        @property
        def root(self) -> str:
            return self._root
        
        @property
        def name(self) -> str:
            return self._name
        
        @property
        def watch(self) -> str:
            return self._watch

    @staticmethod
    def get_current_files(path: str) -> List[Tuple[str, str]]:
        # This will recursively go down each single folder under our path folder
        # and fetch all the files
        curr_f = list()
        for root, _, files in walk(path):
            for file in files:
                curr_f.append((root, file))
        return curr_f


    @staticmethod
    def watch(path: str, queue: Queue, logger, sleeper, interval: int = 5) -> None:

        """
        Watches a given path and tracks all the files in that path directory.
        For every interval, if a file is new, it is added into the queue. Otherwise, it is ignored.

        Parameters:
            path - path to watch
            queue - queue to add to
            logger - LoggingUtils object (not marked for dep reasons)
            sleeper - SleepUtils (not marked for dep reasons)

        """
        signal(SIGINT, sigint_handler)
        DEBUG_LOG_COLOR = logger.LCYAN
        INFO_LOG_COLOR = logger.LGREEN

        completed_files = set()

        logger.warning("Starting Mihari file watcher - this function will not terminate", color=DEBUG_LOG_COLOR)
        while True:

            curr_files = Mihari.get_current_files(path)

            # Remove any files that aren't in current
            # The difference of any files in completed but not in curr
            # are the files that were deleted since the last run

            for rf in completed_files.difference(set(curr_files)):
                logger.debug("File token {} was deleted from disk, deleting from completed tracker".format(rf), color=DEBUG_LOG_COLOR)
                completed_files.discard(rf)

            # Process any new files encountered
            for file in curr_files:
                if file in completed_files:
                    logger.debug("File token {} found on disk, but is already completed - skipping".format(file), color=DEBUG_LOG_COLOR)
                    continue
                else:
                    logger.debug("File token {} found on disk, isn't completed - processing and adding to completed tracker".format(file), color=DEBUG_LOG_COLOR)
                    completed_files.add(file)

                    # Create a MihariEvent for it
                    queue.put(Mihari.MihariEvent(join(file[0], file[1]), file[0], file[1], path))
                    logger.info("Creating new MihariEvent for {} and adding to queue".format(file), color=INFO_LOG_COLOR)

            sleeper.sleep(5, show_logs = False)

if __name__ == "__main__":

    from dep.LoggingUtils import LoggingUtils
    from dep.SleepUtils import SleepUtils

    Mihari.watch("", Queue(), LoggingUtils, SleepUtils, 5)