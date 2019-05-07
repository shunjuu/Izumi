import sys
import os

import anitopy
import pprint
import requests
import urllib

# Hisha3 is a much simpler version of hisha2 that doesn't scan for
# pointless fields

ANILIST_URL = "https://graphql.anilist.co"
KITSU_URL = "https://kitsu.io/api/edge/anime?filter[text]="

STATUSES = ["RELEASING", "FINISHED", "NOT_YET_RELEASED"]

query = '''
query ($search: String, $status: MediaStatus) {
    Media(search: $search, status: $status) {
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

def _post(base, query, vars):
    res = requests.post(base, json={'query': query, 'variables': vars})
    return res

def _hisha(names):
    """
    For the automated airing system, _hisha() will try and find the correct show name.
    Returns the entire json as hisha() and hisha2() return different kinds of results.

    Params:
        names: A (str, str, str) that contains the various names of a show.

    Raises Exception() if no shows are found.

    Raise sys.exit() exception if Anilist fails to connect
    """

    for status in STATUSES:
        for name in names:
            if name:
                try:
                    rvars = {'search': name, 'status': status}
                    res = _post(ANILIST_URL, query, rvars)

                    if res.status_code == 200:
                        return res
                except requests.exceptions.ConnectionError:
                    print("connection error occured")
                    sys.exit()
                except Exception as e:
                    print("general exception")
                    print(e)
                    sys.exit()
    raise Exception("No result found.")



def hisha(episode, title="userPreferred"):
    # returns the show name
    data = anitopy.parse(episode)
    names = _names(data['anime_title'])

    res = _hisha(names)
    return res.json()['data']['Media']['title'][title]


def hisha2a(show):
    # Is provided the right show name, this just gets the information
    names = _names(show)
    res = _hisha(names)
    return res.json()['data']['Media']


def hitsu2a(show):
    """
    Same as hitsu, but accepts a show name
    """
    
    kitsu = show.lower()
    kitsu = urllib.parse.quote(kitsu)

    request_string = KITSU_URL + kitsu
    try:
        ritsu = requests.get(request_string)
        return ritsu.json()
    except:
        sys.exit()

        raise Exception()

if __name__ == "__main__":
    pprint.pprint(hisha2a(sys.argv[1]))