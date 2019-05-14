ANILIST_API_URL = "https://graphql.anilist.co"

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