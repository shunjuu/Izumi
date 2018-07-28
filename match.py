import re
import sys, os
import anitopy
import pprint as pp

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def match(sub14):
    print(bcolors.HEADER + "Show name: " + bcolors.OKBLUE + sub14 + bcolors.ENDC)
    print()
    p = anitopy.parse(sub14)
#    pp.pprint(p)
#    print()

    new_file = p['anime_title'] + " - " + p['episode_number']

    # We want to mark an uncensored video as uncensored
    # Short-circuits :)
    if 'other' in p and 'uncensored' in p['other'].lower():
        new_file = new_file + " (Uncensored)"

    # Video res may not be included
    # Don't use try cause of persistent state changes
    if 'video_resolution' in p:
        new_file = new_file + " [" + p['video_resolution'] + "]"


    # Add the extension
    new_file = new_file + "." + p['file_extension']

    print(bcolors.OKGREEN + "New filename: " + bcolors.WARNING + new_file)
    print()
    print()

    


#match("[meta] High School DxD Hero - 11 [1080p] [UNCENSORED] [HEVC] [x265] [10bit] [Subbed].mkv")
#match("[Golumpa] Isekai Maou to Shoukan Shoujo no Dorei Majutsu - 04 (Uncensored) [WEB+TV 1080p 10-Bit AAC] [E749BD3B].mkv")
#match("[HorribleSubs] Grand Blue - 01 [1080p].mkv")
#match("[mirrored] Back Street Girls - Gokudolls - 03v2 [9731C07A]")

os.system('clear')
match("[meta] High School DxD Hero - 11 [1080p] [UNCENSORED] [HEVC] [x265] [10bit] [Subbed].mkv")
match("[Golumpa] Isekai Maou to Shoukan Shoujo no Dorei Majutsu - 04 (Uncensored) [WEB+TV 1080p 10-Bit AAC] [E749BD3B].mkv")
match("[HorribleSubs] Grand Blue - 01 [1080p].mkv")
match("[mirrored] Back Street Girls - Gokudolls - 03v2 [9731C07A].mkv")



