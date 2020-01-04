#pylint: disable=import-error

import sys
import os

import re
import logging
import requests
import pprint

from src.shared.factory.utils.LoggingUtils import LoggingUtils

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
        studios {
            edges {
                isMain
                node {
                    name
                    siteUrl
                }
            }
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
            studios {
                edges {
                    isMain
                    node {
                        name
                        siteUrl
                    }
                }
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
        self._studio = "Unknown"
        self._studio_url = ""

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
    def idKitsu(self):
        return self._idKitsu

    @idKitsu.setter
    def idKitsu(self, val):
        if val: self._idKitsu = val
    
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

    @property
    def studio(self):
        return self._studio

    @studio.setter
    def studio(self, val):
        if val: self._studio = str(val)

    @property
    def studio_url(self):
        return self._studio_url

    @studio_url.setter
    def studio_url(self, val):
        if val: self._studio_url = str(val)

class Hisha:
    """
    Hisha is a standalone module that handles accurately getting
    actively airing show information from Anilist. 

    # Note: This module is only tested to work with non-UTF8 text
    """

    def __init__(self):

        self._API_URL = ANILIST_API_URL
        self._SINGLE_QUERY = ANILIST_SINGLE_QUERY
        self._PAGE_QUERY = ANILIST_PAGE_QUERY

    def _check_equality_regex(self, str1, str2):
        """
        Checks for equality of two strings without considering punctuation
        Returns a boolean to indicate equality
        """

        LoggingUtils.debug("Comparing {} and {} without punctuation".format(str1, str2))

        try:
            # Anilist sometimes has weird leading/trailing spaces
            re_str1 = re.sub(r'[^\w]','', str1)
            re_str2 = re.sub(r'[^\w]','', str2)
            return bool(re_str1 == re_str2)
        except:
            return False

    def _clean_string(self, str1):
        """
        Cleans a string of potentially problematic characters
        """
        try:
            clean_str = str1.replace('"', '')
            LoggingUtils.debug("Cleaned {} to {}".format(str1, clean_str))
            return clean_str
        except:
            LoggingUtils.debug("Cleaner was not provided a valid title, returning None")
            return None

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
                LoggingUtils.warning("Anilist returned a bad HTTP code when attempting to connect")
                raise Exception()

            try:
                # Try to get the response as a JSON object
                ani_json = ani.json()
            except:
                LoggingUtils.warning("Anilist response did not properly parse into JSON", color=LoggingUtils.YELLOW)
                raise Exception()

            # Return the data provided by the request response
            return ani_json['data']

        except:

            LoggingUtils.error("There was an error when attempting to contact Anilist", color=LoggingUtils.RED)
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
            LoggingUtils.debug("No data provided for {} in {}, returning None".format(search, status))
            return None

        # If any of the titles match, return the show data
        for title in info['Media']['title'].values():
            if self._check_equality_regex(search, title):
                LoggingUtils.debug("Matched {} to {}".format(search, title))
                return info['Media']
            else:
                LoggingUtils.debug("Didn't match {} to {}".format(search, title))

        # If any of the synonyms match, return the show data
        for title in info['Media']['synonyms']:
            if self._check_equality_regex(search, title):
                LoggingUtils.debug("Matched {} to {}".format(search, title))
                return info['Media']
            else:
                LoggingUtils.debug("Didn't match {} to {}".format(search, title))

        # But if none of the titles match, return None
        LoggingUtils.debug("Didn't find a match for {} in {}".format(search, status))
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
            LoggingUtils.debug("No data provided for {} in {}, returning None".format(search, status))
            return None

        # Match against the titles provided in the response
        for show in info:

            # Match against the titles
            for title in show['title'].values():
                if self._check_equality_regex(search, title):
                    LoggingUtils.info("Matched {} to {}".format(search, title))
                    return show
                else:
                    LoggingUtils.debug("Didn't match {} to {}".format(search, title))

            # Match against the synonyms
            for title in show['synonyms']:
                if self._check_equality_regex(search, title):
                    LoggingUtils.info("Matched {} to {}".format(search, title))
                    return show
                else:
                    LoggingUtils.debug("Didn't match {} to {}".format(search, title))

        # If there are no matches, return None
        LoggingUtils.debug("Didn't find a match for {} in {}".format(search, status))
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
        LoggingUtils.debug("Created Kitsu url - {}".format(request_url))

        try:
            kitsu_res = requests.get(request_url)

            try:
                kitsu_res_json = kitsu_res.json()
            except:
                LoggingUtils.warning("Kitsu response did not properly parse into JSON", color=LoggingUtils.YELLOW)
                raise Exception()

            return kitsu_res_json

        except:
            LoggingUtils.error("There was an error when attempting to contact Kitsu", color=LoggingUtils.RED)
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

    def _get_main_studio_info(self, studios):
        """
        Goes through the studio edges and returns the main (studio name, siteurl)

        Params:
            studios - The studios body from the Anilist GraphQL json response

        Returns: A tuple (studio name: str, site url: str), or None if not found
        """
        try:
            edges = studios['edges']
            for edge in edges:
                LoggingUtils.debug("Checking edge {}".format(edge['node']['name']))
                if edge['isMain']:
                    LoggingUtils.debug("Found main studio edge, returning tuple")
                    node = edge['node']
                    return (node['name'], node['siteUrl'])
            # If a main studio isn't found, return None
            LoggingUtils.debug("Didn't find any main studio edge, returning None")
            return None
        except:
            LoggingUtils.warning("Didn't find any main studio edge, returning None", color=LoggingUtils.YELLOW)
            return None

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
            hishaInfo.title = self._clean_string(title)
            hishaInfo.title_native = self._clean_string(title)
            hishaInfo.title_english = self._clean_string(title)
            hishaInfo.title_romaji = self._clean_string(title)
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
            hishaInfo.title = self._clean_string(show['title']['userPreferred'])
            hishaInfo.title_native = self._clean_string(show['title']['native'])
            hishaInfo.title_english = self._clean_string(show['title']['english'])
            hishaInfo.title_romaji = self._clean_string(show['title']['romaji'])
            hishaInfo.startYear = show['startDate']['year']
            hishaInfo.endYear = show['endDate']['year']
            hishaInfo.studio, hishaInfo.studio_url = self._get_main_studio_info(show['studios'])

        return hishaInfo

    def search(self, show):
        """
        Searches for a show and returns its information from Anilist
        """
        airing = self._single_search(show, "RELEASING")
        if airing:
            LoggingUtils.info("Creating HishaInfo for {} in RELEASING".format(show))
            return self._create_hisha_info(airing, show)

        finished = self._page_search(show, "FINISHED")
        if finished:
            LoggingUtils.info("Creating HishaInfo for {} in FINISHED".format(show))
            return self._create_hisha_info(finished, show)

        not_yet_released = self._single_search(show, "NOT_YET_RELEASED")
        if not_yet_released:
            LoggingUtils.info("Creating HishaInfo for {} in NOT_YET_RELEASED".format(show))
            return self._create_hisha_info(not_yet_released, show)

        # None of the three found a result, so create a dummy Hisha object and return it
        LoggingUtils.info("Creating HishaInfo for {} with default values".format(show))
        return self._create_hisha_info(None, show)
