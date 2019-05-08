import os
import sys

import requests
import logging
import pprint

RED = "\033[91m"
GREEN = "\033[32m"
CYAN = "\033[0;96m"
ENDC = "\033[0m"

logging.basicConfig(format="[%(name)s] (%(levelname).4s) %(message)s")

# This is the request query made to Anilist to get a user's anime list
USER_ANIME_QUERY = '''
query ($userName: String) {
    MediaListCollection(userName: $userName, type: ANIME) {
        lists {
            name
            entries {
                media {
                    title {
                        romaji
                        english
                        native
                        userPreferred
                    }
                }
            }
        }
    }
}
'''

class Kishi:

    """
    Kishi is a self-contained module that can determine whether or not
    a given show is being watched by an Anilist user, returning a Boolean.
    """

    def __init__(self, loglevel=logging.INFO):

        self._ANILIST_API_URL = "https://graphql.anilist.co"
        self._ANILIST_USER = USER_ANIME_QUERY

        self._logger = logging.getLogger("Kishi")
        self._logger.setLevel(loglevel)

        # No need for an inner class that represents each show

    def _kishi_list(self, user):
        """
        Helper method to get all of a user's anime list.

        Params:
            user: String, username of Anilist user

        Returns: A tuple of three lists.
            The first list is all the Watching
            The second list is all the PTW
            The third list is all the Paused
        """

        watching = list()
        ptw = list()
        paused = list()
 
        # Anilist API is much nicer to play with. 
        try:
            # Make the request to Anilist, and pass in the userName as the user query
            anilist_res = requests.post(self._ANILIST_API_URL,
                json={'query': self._ANILIST_USER, 'variables': {'userName': user}})

            if anilist_res.status_code != 200:
                self._logger.error("Anilist returned a bad status code when attempting to get {}'s lists".format(user))
                raise Exception()

            try:
                anilist_res_json = anilist_res.json()
            except:
                self._logger.error("Anilist returned a response that was not parseable into JSON")
                raise Exception()

        except:
            self._logger.critical("Kishi was unable to properly contact Anilist")
            raise Exception()
            




if __name__ == "__main__":
    k = Kishi()
    k._kishi_list("aleytia")
