import sys
import os

from src.config import ConfigHandler
from src.argument import ArgumentHandler

def main():

    c = ConfigHandler()
    a = ArgumentHandler(c)
    #a.load_inote(sys.argv[1])


if __name__ == "__main__":
    main()