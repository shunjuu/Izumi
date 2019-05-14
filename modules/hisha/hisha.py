import sys
import os

import re
import logging
import requests

import hisha_constants as hc
        
logging.basicConfig(format="[%(name)s] (%(levelname).4s) %(message)s")

class Hisha:
    """
    Hisha is a standalone module that handles accurately getting
    actively airing show information from Anilist. 

    # Note: This module is only tested to work with non-UTF8 text
    """

    def __init__(self, loglevel=logging.INFO):

        self._API_URL = hc.ANILIST_API_URL
        self._SINGLE_QUERY = hc.ANILIST_SINGLE_QUERY
        self._PAGE_QUERY = hc.ANILIST_PAGE_QUERY

        self._logger = logging.getLogger("Hisha")
        self._logger.setLevel(loglevel)

    def _check_equality_regex(self, str1, str2):
        """
        Checks for equality of two strings without considering punctuation
        Returns a boolean to indicate equality
        """

        self._logger.debug("Comparing {} and {} without punctuation".format(str1, str2))

        try:
            re_str1 = re.sub(r'[^\w\s]','', str1)
            re_str2 = re.sub(r'[^\w\s]','', str2)
            return bool(re_str1 == re_str2)
        except:
            return False

    def _anilist(self, query, search, status):
        """
        This helper method handles making requests to Anilist
        Returns the response in JSON form

        Params:
            query: The type of query (single, page) to request for
            search: the name of the show to search for
            status: the status of the show to search for
        """ 
        try:
            # Make request to Anlist and substitute the variables properly
            ani = requests.post(self._API_URL,
                json={'query': query,
                    'variables': {
                        'search': search, 
                        'status': status}
                })

            if ani.status_code != 200:
                self._logger.error("Anilist returned a bad HTTP code when attempting to connect")
                raise Exception()

            try:
                # Try to get the response as a JSON object
                ani_json = ani.json()
            except:
                self._logger.error("Anilist response did not properly parse into JSON")
                raise Exception()

            # Return the data provided by the request response
            return ani_json['data']

        except:

            self._logger.error("There was an error when attempting to contact Anilist")
            raise Exception()

    def _single_search(self, search, status):
        """
        Searches for a show using the single query
        Params:
            search - show to search for
            status - status to filter under

        Returns: The show data if it's found, or None otherwise
        """
        try:
            info = self._anilist(self._SINGLE_QUERY, search, status)
        except:
            info = str()

        # If any of the titles match, return the show data
        for title in info['Media']['title'].values():
            if self._check_equality_regex(search, title):
                self._logger.debug("Matched {} to {}".format(search, title))
                return info

        # But if none of the titles match, return None
        return None

    def _page_search(self, search, status):
        """
        Searches for a show using the page query
        Params:
            search - show to search for
            status - status to filter under

        Returns: the individual show data if it's found, or None otherwise
        """
        try:
            info = self._anilist(self._PAGE_QUERY, search, status)['Page']['media']
        except:
            # Default to an empty list if the results are bad - Hisha can cleanly exit here
            info = list()

        for show in info:
            for title in show['title'].values():
                if self._check_equality_regex(search, title):
                    self._logger.debug("Matched {} to {}".format(search, title))
                    return show

        # If there are no matches, return None
        return None


    def search(self, show):
        """
        Searches for a show and returns its information from Anilist
        """
        airing = self._single_search(show, "RELEASING")
        if airing:
            # Create a Hisha object and return it
            return airing

        finished = self._page_search(show, "FINISHED")
        if finished:
            # Create a Hisha object and return it
            return finished

        not_yet_released = self._single_search(show, "NOT_YET_RELEASED")
        if not_yet_released:
            # Create a Hisha object and return it
            return not_yet_released

        # None of the three found a result, so create a dummy Hisha object and return it
        return # dummy


if __name__ == "__main__":

    h = Hisha(loglevel=logging.DEBUG)
    print(h.search(sys.argv[1]))
