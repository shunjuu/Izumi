#pylint: disable=import-error

import os
import sys

import re
import requests
import pprint

from src.shared.factory.utils.LoggingUtils import LoggingUtils

RED = "\033[91m"
GREEN = "\033[32m"
CYAN = "\033[0;96m"
ENDC = "\033[0m"

# This is the request query made to Anilist to get a user's anime list
USER_ANIME_QUERY = '''
query ($userName: String) {
    MediaListCollection(userName: $userName, type: ANIME) {
        lists {
            name
            entries {
                media {
                    id
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

    def __init__(self):

        self._ANILIST_API_URL = "https://graphql.anilist.co"
        self._ANILIST_USER = USER_ANIME_QUERY

        # No need for an inner class that represents each show

    def _check_equality_regex(self, str1, str2):
        """
        Checks for equality of two strings without considering punctuation
        Returns a boolean to indicate equality
        """

        LoggingUtils.debug("Comparing {} and {} without punctuation".format(str1, str2))

        try:
            re_str1 = re.sub(r'[^\w\s]','', str1)
            re_str2 = re.sub(r'[^\w\s]','', str2)
            return bool(re_str1 == re_str2)
        except:
            return False

    def _add_list_entries(self, list_name, list_json):
        """
        Helper method to add all list entries into a medialist (watching/paused/ptw)
        Params:
            list_name: the name that the list appears to be from Anilist ("Watching")
            list_json: anilist's raw api response (json format) {'data':'MediaListCollection'}

        Returns: A list with populated Anilist Media entries (a list of dicts)
        """
        try:

            entries = list()

            media_lists = list_json['data']['MediaListCollection']['lists']
            for media_list in media_lists:
                if list_name.lower() == media_list['name'].lower():
                    for entry in media_list['entries']:
                        entries.append(entry['media'])

            return entries

        except:
            LoggingUtils.warning("Kishi was unable to process list entries for {}".format(list_name), color=LoggingUtils.YELLOW)
            raise Exception()

    def _kishi_list(self, user):
        """
        Helper method to get all of a user's anime list.

        Params:
            user: String, username of Anilist user

        Returns: A tuple of three lists.
            The first list is all the Watching
            The second list is all the PTW
            The third list is all the Paused

        Throws an exception if anything goes wrong. This should be caught by any method using this.
        """

        watching = list()
        paused = list()
        ptw = list()
 
        # Anilist API is much nicer to play with. 
        try:
            # Make the request to Anilist, and pass in the userName as the user query
            anilist_res = requests.post(self._ANILIST_API_URL,
                json={'query': self._ANILIST_USER, 'variables': {'userName': user}})

            if anilist_res.status_code != 200:
                LoggingUtils.debug("Anilist returned a bad status code when attempting to get {}'s lists".format(user))
                raise Exception()

            try:
                anilist_res_json = anilist_res.json()
            except:
                LoggingUtils.debug("Anilist returned a response that was not parseable into JSON")
                raise Exception()

            watching = self._add_list_entries("Watching", anilist_res_json)
            paused = self._add_list_entries("Paused", anilist_res_json)
            ptw = self._add_list_entries("Planning", anilist_res_json)

        except:
            LoggingUtils.warning("Kishi was unable to properly contact Anilist", color=LoggingUtils.YELLOW)
            raise Exception()
            
        return (watching, paused, ptw)


    def is_user_watching_names(self, user, show_name):
        """
        Determines whether or not an Anilist user is watching a show
        Checks by show name

        Params:
            user: username to look up
            show_name: name of the show to look up. this should already be the anilist name.

        Returns: a boolean - True if watching, False if not
        """
        try:
            watching, paused, ptw = self._kishi_list(user)

            for show in watching:
                for title in show['title'].values():
                    if self._check_equality_regex(title, show_name):
                        LoggingUtils.debug("Matched {} to {} in {}".format(title, show_name, "watching"))
                        return True 

            for show in paused:
                for title in show['title'].values():
                    if self._check_equality_regex(title, show_name):
                        LoggingUtils.debug("Matched {} to {} in {}".format(title, show_name, "paused"))
                        return True 

            for show in ptw:
                for title in show['title'].values():
                    if self._check_equality_regex(title, show_name):
                        LoggingUtils.debug("Matched {} to {} in {}".format(title, show_name, "planning"))
                        return True 

            LoggingUtils.debug("Didn't find a match for {}".format(show_name))
            return False

        except:
            # If any errors are encountered, return True (default assumption)
            LoggingUtils.warning("An error was encountered while contacting Anilist. Defaulting to TRUE", color=LoggingUtils.YELLOW)
            return True

    def is_user_watching_id(self, user, show_id):
        """
        Determines whether or not an Anilist user is watching a show
        Checks by show ID

        Params:
            user: username to look up
            id: id of the show to look up

        Returns: a boolean - True if watching, False if not
        """

        try:
            show_id = int(show_id) # Get the int equivalent value of the ID
        except:
            # Why would you not pass an integer in?
            LoggingUtils.warning("Kishi ID search requires an input that can be converted to an int. Returning FALSE",
                color=LoggingUtils.YELLOW)
            return False

        try:

            watching, paused, ptw = self._kishi_list(user)

            for show in watching:
                if show_id == show['id']:
                    LoggingUtils.debug("Found show ID {} in {}".format(show_id, "watching"))
                    return True

            for show in paused:
                if show_id == show['id']:
                    LoggingUtils.debug("Found show ID {} in {}".format(show_id, "paused"))
                    return True

            for show in ptw:
                if show_id == show['id']:
                    LoggingUtils.debug("Found show ID {} in {}".format(show_id, "planning"))
                    return True

            LoggingUtils.debug("Didn't find a match for {}".format(show_id))
            return False

        except:
            # If any errors are encountered, return True (default assumption)
            LoggingUtils.warning("An error was encountered while contacting Anilist. Defaulting to TRUE", color=LoggingUtils.YELLOW)
            return True
