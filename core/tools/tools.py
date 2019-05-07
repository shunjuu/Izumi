import os
import sys

import pprint as pp

# lib imports
from lib import hisha2

# src imports
from src.config import Config
from src import move # Mode 1, for moving shows
from src import rmdir # Mode 2, for removing empty directories
from src import rename # Mode 3, for renaming files in directories recursively
from src import season # Mode 4, moving existing files into a subdirectory for Season
from src import delete # Mode 5, delete an existing show from the system

# Options text
OPTIONS = """
    1. Move Airing shows to Premiered
    2. Remove empty directories
    3. Rename existing episodes to the general style
    4. Move an existing folder into a seasonal subdirectory
    5. Rename a single folder
    6. Delete a show

Choice: """

def main():
    """
    Ask the User what they'd like to do. Call appropriate module as requested.
    """

    # Prompt for input
    while True:
        print("\nWhat would you like to do? (Enter \"1\", \"2\", etc...)")
        try:
            mode = input(OPTIONS)
        except:
            print("Exiting...")
            sys.exit(1)

        # Make sure input is only an integer
        try:
            mode = int(mode)
        except:
            print("Error: Please enter a number.")

        if mode not in range(1, 7):
            print("Error: Please input a valid number.")

        # Load the config
        conf = Config()

        # Start handling the modes
        if mode is 1:
            move.move(conf)
        elif mode is 2:
            rmdir.rmdir(conf)
        elif mode is 3:
            rename.rename_mass(conf)
        elif mode is 4:
            season.season(conf)
        elif mode is 5:
            rename.rename_single(conf)
        elif mode is 6:
            delete.delete(conf)
            


if __name__ == "__main__":
    main()
