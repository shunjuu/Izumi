import sys
import os

import pprint as pp

from enum import Enum # We're going to use this to define GraphQL Classes
from collections import defaultdict
from datetime import datetime

# Dependencies
import requests
import anitopy

import urllib.parse # For hitsu

anilist_url = "https://graphql.anilist.co"
kitsu_url = "https://kitsu.io/api/edge/anime?filter[text]="

# Anilist GraphQL Enum Definitions

# Define MediaType
class MediaType(Enum):
    anime = "ANIME"
    manga = "MANGA"

# Define MediaStatus
class MediaStatus(Enum):
    releasing = "RELEASING"
    finished = "FINISHED"
    not_yet_released = "NOT_YET_RELEASED"
    cancelled = "CANCELLED"

# Define MediaFormat
class MediaFormat(Enum):
    tv = "TV"
    tv_short = "TV_SHORT"
    ova = "OVA"
    ona = "ONA"
    movie = "MOVIE"
    special = "SPECIAL"
    one_shot = "ONE_SHOT"
    music = "MUSIC"
    manga = "MANGA"
    novel = "NOVEL"

# Define MediaSeason
class MediaSeason(Enum):
    winter = "WINTER"
    spring = "SPRING"
    summer = "SUMMER"
    fall = "FALL"

# Generic GraphQL request

# Standard GraphQL query format; use query and vars for var autofill (or lack thereof safety)
rquery = '''
query ($search: String, $tp: MediaType, $st: MediaStatus, $ft: MediaFormat, $sn: MediaSeason, $snY: Int) {
    Media(search: $search, type: $tp, status: $st, format: $ft, season: $sn, seasonYear: $snY) {
        id
        idMal
        episodes
        duration
        popularity
        averageScore
        bannerImage
        coverImage {
            large
        }
        title {
            userPreferred
            native
        }
        startDate {
            year
        }
        endDate {
            year
        }
    }
}
'''

seasons = {
    1: MediaSeason.winter,
    2: MediaSeason.winter,
    3: MediaSeason.spring,
    4: MediaSeason.spring,
    5: MediaSeason.spring,
    6: MediaSeason.summer,
    7: MediaSeason.summer,
    8: MediaSeason.summer,
    9: MediaSeason.fall,
    10: MediaSeason.fall,
    11: MediaSeason.fall,
    12: MediaSeason.winter
}

# Hisha order of requests
HISHA_TYPE = [MediaType.anime]

HISHA_STATUS = [
        MediaStatus.releasing,
        MediaStatus.finished,
        MediaStatus.not_yet_released
]

HISHA_FORMAT = [
        MediaFormat.tv, 
        MediaFormat.tv_short, 
        MediaFormat.ona, 
        MediaFormat.ova, 
        MediaFormat.movie, 
        MediaFormat.special
]

def get_time():
    """
    Uses datetime to get the current year and month
    Returns (month, year) as a tuple of all ints
    """
    date = datetime.today()
    return (date.month, date.year)

def get_season():
    """
    Returns the season type AS A STRING
    """
    month = get_time()[0] # Get the month

    # Too bad there's no switch cases
    return seasons[month].value


def _fill_vars(search, tp, st, ft, sn=None, snY=None):
    """
    Build the variables dictionary to be sent with the query
    """
    variables = {
        'search': search, # search 
        'tp': tp, # type 
        'st': st, # status
        'ft': ft, # format
    }

    # We could leave them as Nonetype, but exclude for safety
    if sn:
        variables['sn'] = sn
    if snY:
        variables['snY'] = str(snY)

    return variables

def post(base, query, variables):
    """
    Send a crafted post request out to Anilist
    """
    res = requests.post(base, json={'query': query, 'variables': variables})
    return res

def _names(show):

    # Make last remove the last word
    last = show.rsplit(' ', 1)[0]

    # Colon replaces first " - " to ": " and removes other " - "
    col = show.replace(" - ", ": ", 1)
    col = col.replace(" - ", "")
    # Edge case, it might end with one too
    if col.endswith(" -"):
        col = col[:-2].strip()

    # But if there's no change, leave it alone
    if col == show: col = None

    return (show, last, col)

def _hisha(names):
    """
    For the automated airing system, _hisha() will try and find the correct show name.
    Returns the entire json as hisha() and hisha2() return different kinds of results.

    Params:
        names: A (str, str, str) that contains the various names of a show.

    Raises Exception() if no shows are found.

    Forces an application exit (os, not sys) if Anilist fails to connect
    """

    for tp in HISHA_TYPE:
        for name in names:
            if name:
                for st in HISHA_STATUS:
                    for ft in HISHA_FORMAT:
                        try:
                            # We're using enum types, use values
                            rvars = _fill_vars(name, tp.value, st.value, ft.value)
                            res = post(anilist_url, rquery, rvars)

                            # 404 won't throw exception, only bad connection
                            # Thus, we only need to check for 200
                            if res.status_code == 200:
                                return res

                        except requests.exceptions.ConnectionError:
                            print("There appears to be no internet connection.")
                            print("Now exiting...")
                            raise Exception()

                        except:
                            print("An exception occured when attempting to contact Anilist.")
                            print("Now exiting...")
                            raise Exception()

    # If we've reachedt his point, we didn't find a result
    raise Exception("No result found.")

def hisha(episode, title="userPreferred"):
    """
    The default Hisha module, for standard airing cases. This will attempt to find
    the show in airing, and then not_yet_aired, and then premiered.

    It also tries multiple versions of the search:
        1. Last word removed (i.e., some kind of Season indicator)
        2. Replace the first " - " to ": " and remove the other " - "

    Forces os-level application exit if _hisha fails to find a show.
    """
    data = anitopy.parse(episode)
    names = _names(data['anime_title'])

    # Get the show name with the helper.
    try:
        res = _hisha(names)
    except:
        # An exception will be thrown if nothing was found. We exit if that's the case.
        print("No show was found when searching. The system will now exit.")
        raise Exception()

    # Backwards-compatability: Hisha will return the title
    return res.json()['data']['Media']['title'][title]


def hisha2(episode):
    """
    Hisha2, unlike hisha, simply returns all the json it gets.
    """
    data = anitopy.parse(episode)
    names = _names(data['anime_title'])

    try:
        res = _hisha(names)
    except:
        # An exception will be thrown if nothing was found. We exit if that's the case.
        print("No show was found when searching. The system will now exit.")
        raise Exception()
    return res.json()

def hisha2a(show):
    """
    hisha2a doesn't use anitopy to parse the show name - it's PROVIDED the (correct) show name
    """

    # Even though we have the right names, generate new ones anyway
    names = _names(show)

    try:
        res = _hisha(names)
        return res.json()['data']['Media']
    except:
        print("No show was found when searching. The system will now exit.")
        raise Exception()



def hitsu(episode):
    """
    Hitsu returns the Kitsu.io queries, since they are separate.
    Very basic, just searches for what is given.
    """
    data = anitopy.parse(episode)
    kitsu = data['anime_title'].lower()
    kitsu = urllib.parse.quote(kitsu)

    request_string = kitsu_url + kitsu
    try:
        ritsu = requests.get(request_string)
        return ritsu.json()

    except requests.exceptions.ConnectionError:
        print("There appears to be no internet connection.")
        print("Now exiting...")
        raise Exception()

    except:
        print("Fatal exception encountered when attempting to contact Kitsu.")
        print("Now exiting...")
        raise Exception()

    # Hitsu is in beta, right now we don't want an Exeption()
    return None

def hitsu2a(show):
    """
    Same as hitsu, but accepts a show name
    """
    
    kitsu = show.lower()
    kitsu = urllib.parse.quote(kitsu)

    request_string = kitsu_url + kitsu
    try:
        ritsu = requests.get(request_string)
        return ritsu.json()

    except requests.exceptions.ConnectionError:
        print("There appears to be no internet connection.")
        print("Now exiting...")
        raise Exception()

    except:
        print("Fatal exception encountered when attempting to contact Kitsu.")
        print("Now exiting...")
        raise Exception()

    # Hitsu is in beta, right now we don't want an Exeption()
    return None
