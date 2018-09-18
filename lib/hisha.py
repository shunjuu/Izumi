"""
Hisha is a small program to determine the "correct" show name of an anime episode.
While most shows are in the correct format, several shows may not have the right
name, and Anilist GraphQL queries will thus return null.

This app will attempt to return the correct name of a show.
"""

# Standard imports
import sys, os
import pprint as pp
from enum import Enum
from collections import defaultdict

# Dependencies
import requests # for pinging anilist
import anitopy  # for breaking down show names

# Print colors
class colors:
    """
    Shell based colors for colored printing!
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    GREEN = '\033[32m'
    WARNING = '\033[93m'
    LCYAN = '\033[0;96m'
    ORANGE = '\033[0;33m'
    MAGENTA = '\033[35m'
    LMAGENTA = '\033[95m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Anilist URL
ANILIST_URL = "https://graphql.anilist.co"

# The generic GraphQL request string
QUERY = '''
{{
	Media(search:"{title}" type:{tp} status:{st} format:{ft}) {{
		title {{
			romaji
                        english
			native
                        userPreferred
		}}
	}}
}}'''

# Several lists for the GraphQL query filters
TYPE = ['ANIME']
STATUS = ['RELEASING', 'FINISHED', 'NOT_YET_RELEASED']
FORMAT = ['TV', 'TV_SHORT', 'OVA', 'ONA', 'MOVIE', 'SPECIAL']

# For MediaTitles
class MediaTitle(Enum):
    ALL = "all"
    ROMAJI = "romaji"
    ENGLISH = "english"
    NATIVE = "native"
    PREFER = "userPreferred"


def request_anilist(show):
    """
    Sends a series of requests to Anilist and returns the dict if found.
    If not, returns a dict with all the fields set to None.
    """

    t = TYPE[0]

    # Basically we just need to check every option, in the order presented
    for s in STATUS: 
        for f in FORMAT:
            curr_query = QUERY.format(title=show, tp=t, st=s, ft=f)
            try:
                r = requests.post(ANILIST_URL, json={'query':curr_query})
                if r.status_code == 200:
                    return r.json()['data']['Media']['title']
            except:
                print(colors.FAIL + "WARNING: " + colors.ENDC +
                        "There was an error when attempting to contact Anilist.")
                sys.exit(-1)

    # If we've gotten to this point, we raise an exception
    raise Exception("No result found.")


def hisha(episode, mediaTitle=MediaTitle.PREFER):
    """
    A single function to get the correct show name.

    Args: 
        episode: A string that is the name of the episode. 
        mediaTitle: The format of the MediaTitle.
        err: Determines what should be returned in event of no result.

        Episode names don't have to be "clean."

    Returns: 
        The correct show name if it exists, or ret type.
    """

    # Parse the data and assign the show name
    episode_data = anitopy.parse(episode)
    show = episode_data['anime_title']
    try:
        titles = request_anilist(show)

    except:
        # When we reach this point, there's a chance the show name is bad.
        # If this happens, we first try and remove the last word in the show name
        # i.e., Shingeki no Kyojin S3 -> Shingeki no Kyojin -> Shingeki no Kyojin 3 (Anilist)
        show = show.split(' ')
        show.pop()
        show = ' '.join(show)

        # Now try again
        try:
            titles = request_anilist(show)
        except:
            print(colors.FAIL + "WARNING: " + colors.ENDC +
                    "Show was not found, please try again.")
            sys.exit(-1)

    if mediaTitle == MediaTitle.ALL:
        return titles
    elif mediaTitle == 'all':
        return titles
    else:
        try:
            return titles[mediaTitle.value]
        except:
            try:
                return titles[mediaTitle]
            except:
                print(colors.FAIL + "WARNING: " + colors.ENDC +
                        "Improper mediaTitle argument.")

# Main method in case this is invoked from command line
if __name__ == "__main__":

    # Optional sys_args
    try:
        print(hisha(sys.argv[1]))
    except IndexError:
        print("\n" + colors.FAIL + "WARNING: " + colors.ENDC + 
                "It seems like you did not provide an episode argument.", end="\n\n")
        sys.exit(-1)
    except Exception as e:
        print(e)
        sys.exit(-1)


