import sys
import os

import re
import logging
import requests
import pprint

logging.basicConfig(format="[%(name)s] (%(levelname).4s) %(message)s")

ANILIST_API_URL = "https://graphql.anilist.co"
KITSU_API_URL = "https://kitsu.io/api/edge/anime?filter[text]="

ANILIST_SINGLE_QUERY = '''
query ($search: String, $status: MediaStatus) {
    Media(search: $search, status: $status, type: ANIME) {
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
            english
            romaji
        }
        synonyms
        startDate {
            year
        }
        endDate {
            year
        }
    }
}
'''

ANILIST_PAGE_QUERY = '''
query ($search: String, $status: MediaStatus) {
    Page (page: 1) {
        pageInfo {
            total
            currentPage
        }

        media(search: $search, status: $status, type: ANIME) {
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
                english
                romaji
            }
            synonyms
            startDate {
                year
            }
            endDate {
                year
            }
        }
    }
}
'''

class HishaInfo:
    """
    This is a class that holds the information for a returned show from Hisha.
    Return this instead of a raw dict to streamline data access.
    """

    def __init__(self):
        # Set the default values here
        self._id = -1
        self._idMal = -1
        self._idKitsu = -1
        self._episodes = -1
        self._duration = -1
        self._popularity = -1
        self._averageScore = -1
        self._bannerImage = ""
        self._coverImage = ""
        self._title_userPreferred = "Unknown"
        self._title_native = "Unknown"
        self._title_english = "Unknown"
        self._title_romaji = "Unknown"
        self._startDate_year = -1
        self._endDate_year = -1

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, val):
        if val: self._id = val

    @property
    def idMal(self):
        return self._idMal

    @idMal.setter
    def idMal(self, val):
        if val: self._idMal = val
    
    @property
    def episodes(self):
        return self._episodes

    @episodes.setter
    def episodes(self, val):
        if val: self._episodes = val

    @property
    def duration(self):
        return self._duration
    
    @duration.setter
    def duration(self, val):
        if val: self._duration = val

    @property
    def popularity(self):
        return self._popularity

    @popularity.setter
    def popularity(self, val):
        if val: self._popularity = val

    @property
    def averageScore(self):
        return self._averageScore
    
    @averageScore.setter
    def averageScore(self, val):
        if val: self._averageScore = val 

    @property
    def bannerImage(self):
        return self._bannerImage
   
    @bannerImage.setter
    def bannerImage(self, val):
        if val: self._bannerImage = val 

    @property
    def coverImage(self):
        return self._coverImage
    
    @coverImage.setter
    def coverImage(self, val):
        if val: self._coverImage = val

    @property
    def title(self):
        """Title as a property itself is treated as userPreferred"""
        return self._title_userPreferred
    
    @title.setter
    def title(self, val):
        if val: self._title_userPreferred = val

    @property
    def title_userPreferred(self):
        return self._title_userPreferred
   
    @title_userPreferred.setter
    def title_userPreferred(self, val):
        if val: self._title_userPreferred = val 

    @property
    def title_native(self):
        return self._title_native
    
    @title_native.setter
    def title_native(self, val):
        if val: self._title_native = val

    @property
    def title_english(self):
        return self._title_english
    
    @title_english.setter
    def title_english(self, val):
        if val: self._title_english = val

    @property
    def title_romaji(self):
        return self._title_romaji
    
    @title_romaji.setter
    def title_romaji(self, val):
        if val: self._title_romaji = val

    @property
    def startYear(self):
        return self._startDate_year

    @startYear.setter
    def startYear(self, val):
        if val: self._startDate_year = val

    @property
    def endYear(self):
        return self._endDate_year

    @endYear.setter
    def endYear(self, val):
        if val: self._endDate_year = val

class Hisha:
    """
    Hisha is a standalone module that handles accurately getting
    actively airing show information from Anilist. 

    # Note: This module is only tested to work with non-UTF8 text
    """

    def __init__(self, loglevel=logging.INFO):

        self._API_URL = ANILIST_API_URL
        self._SINGLE_QUERY = ANILIST_SINGLE_QUERY
        self._PAGE_QUERY = ANILIST_PAGE_QUERY

        self._logger = logging.getLogger("Hisha")
        self._logger.setLevel(loglevel)

    def _check_equality_regex(self, str1, str2):
        """
        Checks for equality of two strings without considering punctuation
        Returns a boolean to indicate equality
        """

        self._logger.debug("Comparing {} and {} without punctuation".format(str1, str2))

        try:
            # Anilist sometimes has weird leading/trailing spaces
            re_str1 = re.sub(r'[^\w]','', str1)
            re_str2 = re.sub(r'[^\w]','', str2)
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
            # There wasn't a match, so return None immediately
            self._logger.debug("No data provided for {} in {}, returning None".format(search, status))
            return None

        # If any of the titles match, return the show data
        for title in info['Media']['title'].values():
            if self._check_equality_regex(search, title):
                self._logger.info("Matched {} to {}".format(search, title))
                return info['Media']
            else:
                self._logger.debug("Didn't match {} to {}".format(search, title))

        # If any of the synonyms match, return the show data
        for title in info['Media']['synonyms']:
            if self._check_equality_regex(search, title):
                self._logger.info("Matched {} to {}".format(search, title))
                return info['Media']
            else:
                self._logger.debug("Didn't match {} to {}".format(search, title))

        # But if none of the titles match, return None
        self._logger.debug("Didn't find a match for {} in {}".format(search, status))
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
            self._logger.debug("No data provided for {} in {}, returning None".format(search, status))
            return None

        # Match against the titles provided in the response
        for show in info:

            # Match against the titles
            for title in show['title'].values():
                if self._check_equality_regex(search, title):
                    self._logger.info("Matched {} to {}".format(search, title))
                    return show
                else:
                    self._logger.debug("Didn't match {} to {}".format(search, title))

            # Match against the synonyms
            for title in show['synonyms']:
                if self._check_equality_regex(search, title):
                    self._logger.info("Matched {} to {}".format(search, title))
                    return show
                else:
                    self._logger.debug("Didn't match {} to {}".format(search, title))

        # If there are no matches, return None
        self._logger.debug("Didn't find a match for {} in {}".format(search, status))
        return None

    def _kitsu_basic_search(self, title):
        """
        This is a quick Kitsu search implementation from the Hitsu 2A module.

        Params:
            title - the title of the show (in provided request) to search for

        Returns: Kitsu's JSON response
        """
        title_lower = title.lower()
        request_url = requests.utils.requote_uri(KITSU_API_URL + title_lower)
        self._logger.debug("Created Kitsu url - {}".format(request_url))

        try:
            kitsu_res = requests.get(request_url)

            try:
                kitsu_res_json = kitsu_res.json()
            except:
                self._logger.error("Kitsu response did not properly parse into JSON")
                raise Exception()

            return kitsu_res_json

        except:
            self._logger.error("There was an error when attempting to contact Kitsu")
            raise Exception()

    def _get_kitsu_id(self, title):
        """
        Gets Kitsu's unique ID for a provided show.

        Params:
            title - a title to search for

        Returns: The ID, if it's found, as an int, or -1 otherwise
        """
        try:
            kitsu_id = self._kitsu_basic_search(title)['data'][0]['id']
            return int(kitsu_id)
        except:
            return -1

    def _create_hisha_info(self, show, title):
        """
        Creates a HishaInfo object from a provided show json
        Params:
            show - a dict that represents Anilist show response, or None
            title - the name of the show (for when it's not provided)

        Returns a HishaInfo object
        """

        hishaInfo = HishaInfo()

        if show is None:
            # If the show doesn't exist, set title and use defaults
            hishaInfo.title = title 
            hishaInfo.title_native = title
            hishaInfo.title_english = title
            hishaInfo.title_romaji = title
        else:
            # Don't need to check for None values - setters will handle it
            hishaInfo.id = show['id']
            hishaInfo.idMal = show['idMal']
            hishaInfo.idKitsu = self._get_kitsu_id(title)
            hishaInfo.episodes = show['episodes']
            hishaInfo.duration = show['duration']
            hishaInfo.popularity = show['popularity']
            hishaInfo.averageScore = show['averageScore']
            hishaInfo.bannerImage = show['bannerImage']
            hishaInfo.coverImage = show['coverImage']['large']
            hishaInfo.title = show['title']['userPreferred']
            hishaInfo.title_native = show['title']['native']
            hishaInfo.title_english = show['title']['english']
            hishaInfo.title_romaji = show['title']['romaji']
            hishaInfo.startYear = show['startDate']['year']
            hishaInfo.endYear = show['endDate']['year']

        return hishaInfo

    def search(self, show):
        """
        Searches for a show and returns its information from Anilist
        """
        airing = self._single_search(show, "RELEASING")
        if airing:
            self._logger.info("Creating HishaInfo for {} in RELEASING".format(show))
            return self._create_hisha_info(airing, show)

        finished = self._page_search(show, "FINISHED")
        if finished:
            self._logger.info("Creating HishaInfo for {} in FINISHED".format(show))
            return self._create_hisha_info(finished, show)

        not_yet_released = self._single_search(show, "NOT_YET_RELEASED")
        if not_yet_released:
            self._logger.info("Creating HishaInfo for {} in NOT_YET_RELEASED".format(show))
            return self._create_hisha_info(not_yet_released, show)

        # None of the three found a result, so create a dummy Hisha object and return it
        self._logger.info("Creating HishaInfo for {} with default values".format(show))
        return self._create_hisha_info(None, show)


if __name__ == "__main__":

    h = Hisha(loglevel=logging.DEBUG)
    pprint.pprint(h.search(sys.argv[1]).title)
