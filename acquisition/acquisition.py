import sys
import os

from src.config_handler import ConfigHandler
from src.argument_handler import ArgumentHandler
from src.file_handler import FileHandler

def main():

    c = ConfigHandler()
    a = ArgumentHandler(c)
    a.load_inote(sys.argv[1])
    f = FileHandler(c, a, sys.argv[1])
    print("-------")


if __name__ == "__main__":
    main()
