#pylint: disable=import-error

import os
import sys

import time
import pprint
import requests

from src.shared.factory.utils.LoggingUtils import LoggingUtils

RED = "\033[91m"
GREEN = "\033[32m"
ENDC = "\033[0m"
CYAN = "\033[0;96m"

class Akari:

    """
    A wrapper around Jikan to get user lists
    """

    def __init__(self):

        self._JIKAN_USER_WATCHING = "https://api.jikan.moe/v3/user/{}/animelist/watching/{}"
        self._JIKAN_USER_PTW = "https://api.jikan.moe/v3/user/{}/animelist/plantowatch/{}"

    def _akari_list(self, user, listurl, listname):
        """
        Helper method that gets a user's specific anime list
        !! Doesn't handle the random errors thrown by Jikan.moe

        Params:
            user: String, is the username of the MAL user
            listurl: The URL to use when fetching information
            listname: Watching/Plan To Watch/etc

        Returns a list that holds a bunch of anime entries
        """

        anime = list() # Stores every anime entry that is paginated

        # Step 1: Get the first page (which is assumed to exist)
        try:

            jikan_res = requests.get(listurl.format(user, ""))

            # Check the Status code
            if jikan_res.status_code != 200:
                LoggingUtils.debug("Jikan.moe returned a bad status code when attempting to get {}'s {} list".format(user, listname), color=LoggingUtils.YELLOW)
                raise Exception()

            # Make sure there actually was an anime
            try:
                jikan_res_json = jikan_res.json()
            except:
                jikan_res_json = dict() # For clean handling

            if 'anime' not in jikan_res_json:
                LoggingUtils.debug("Jikan.moe did not have an anime list when attempting to get {}'s {} list page".format(user, listname), color=LoggingUtils.YELLOW)
                raise Exception()

            # Add all anime in the first page
            for entry in jikan_res_json['anime']:
                anime.append(entry)
                LoggingUtils.debug("Added {} show: {}".format(listname, entry['title']))

            # Now, process the rest of pages that are there
            page = 2
            while (len(jikan_res_json['anime']) == 300):

                jikan_res = requests.get(listurl.format(user, str(page)))

                if jikan_res.status_code != 200 or 'anime' not in jikan_res:
                    LoggingUtils.debug("Jikan.moe returned a bad status code when attempting to get {}'s {} list".format(user, listname))
                    raise Exception()

                try:
                    jikan_res_json = jikan_res.json()
                except:
                    jikan_res_json = dict()

                if 'anime' not in jikan_res_json:
                    LoggingUtils.debug("Jikan.moe did not have an anime list when attempting to get {}'s {} list page".format(user, listname))
                    raise Exception()

                for entry in jikan_res_json['anime']:
                    anime.append(entry)
                    LoggingUtils.debug("Added {} show: {}".format(listname, entry['title']))

                page += 1

            return anime

        except:
            # raise some kind of exception - somehow Jikan couldn't be reached
            LoggingUtils.error("Akari encountered an error when attempting to fetch {}'s {} list".format(user, listname), color=LoggingUtils.RED)
            raise Exception()

    def _akari_fetch_retry(self, user, listurl, listname, times=5):
        """
        Jikan.moe is susceptible to randomly failing. This method allows us to try multiple times before really "failing"

        Params: See self._akari_list

        Returns: See self._akari_list if successful, or raises an Exception() otherwise
        """

        for i in range(times):
            try:
                LoggingUtils.debug("Attempt #{} to contact Jikan.moe for {}{}{}".format(i+1, CYAN, listname, ENDC))
                anime = self._akari_list(user, listurl, listname)
                LoggingUtils.debug("Attempt #{} {}succeeded{}".format(i+1, GREEN, ENDC))
                return anime
            except:
                # Sleep 5 seconds, and then try again
                LoggingUtils.debug("Attempt #{} {}failed{}, sleeping 5 seconds and trying again...".format(i+1, RED, ENDC))
                time.sleep(5)

        # If this point is reached, then there has been too many errors. Raise an exception
        LoggingUtils.error("Akari was unable to contact Jikan.moe")
        raise Exception()

    def akari_list(self, user, times=5):
        """
        Gets a user's watching list, in names. 
        This should not be a @classmethod or @staticmethod
        """
        anime = list()
        try:
            jikan_res_watching = self._akari_fetch_retry(user, self._JIKAN_USER_WATCHING, "Watching", times)
            jikan_res_ptw = self._akari_fetch_retry(user, self._JIKAN_USER_PTW, "PTW", times)

            anime.extend(jikan_res_watching)
            anime.extend(jikan_res_ptw)
        except:
            # We couldn't find the user at all, so just return an empty list
            pass

        return anime

    def is_user_watching_names(self, user, show_name, times=5):
        """
        Is a user watching this show or not?

        Params:
            user: username to lookup
            show_name: show name to match against

        Returns True if the show was found in the list, false if not
        """
        LoggingUtils.debug("{}Now finding{} if \"{}\" is in {}'s list".format(CYAN, ENDC, show_name, user))
        anime_list = self.akari_list(user, times)
        for show in anime_list:
            if show['title'] == show_name:
                LoggingUtils.debug("\"{}\" was found in {}'s list".format(show_name, user))
                return True

        LoggingUtils.debug("\"{}\" was not found in {}'s list".format(show_name, user))
        return False

    def is_user_watching_id(self, user, malID, times=5):
        """
        Is a user watching this show or not?

        Params:
            user: username to lookup
            malID: malID to match against
        """
        LoggingUtils.debug("{}Now finding{} if \"{}\" is in {}'s list".format(CYAN, ENDC, malID, user))
        anime_list = self.akari_list(user, times)
        for show in anime_list:
            if str(show['mal_id']) == str(malID):
                LoggingUtils.debug("\"{}\" was found in {}'s list".format(malID, user))
                return True

        LoggingUtils.debug("\"{}\" was not found in {}'s list".format(malID, user))
        return False
