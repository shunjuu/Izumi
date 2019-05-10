import sys
import os

import requests

ANILIST_API_URL = "https://graphql.anilist.co"

# GraphQL Query for Anilist to get information.
# Status is allowed because the last episode might be marked as "Completed"
ANILIST_QUERY = '''
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
        startDate {
            year
        }
        endDate {
            year
        }
    }
}
'''

class Hisha:
    """
    Hisha is a standalone module that handles accurately getting
    actively airing show information from Anilist. 
    """

    def __init__():

        self._API_URL = ANILIST_API_URL
        self._QUERY = ANILIST_QUERY

if __name__ == "__main__":
    x = requests.post(ANILIST_API_URL, 
        json={'query': ANILIST_QUERY, 
                'variables': {'search': "Kimetsu no Yaiba", 'status': 'RELEASING'}})
    print(x.status_code)
    print(x.content)
