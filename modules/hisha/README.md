# Hisha

## Introduction

Hisha (飛車, lit. "rook") is a utility module to fetch \[airing\] anime show information from Anilist.
It accepts a string (that is assumed to be the show's name on Anilist, or a close match thereof), and finds the show information. 
If the show is found, a HishaInfo object is created and returned. If the show is not found, a default HishaInfo object is created and returned.

This module is designed to simplify fetching show information. It is not guaranteed to be 100% accurate, but should be able to fetch airing show information with high confidence. It contains all errors within itself.

## Usage

Hisha has a single public method that returns a HishaInfo object:
- `def search(self, show)`

`def search(self, show)` accepts a single parameter:
- `show` (required): A String that is the same as a given show's name on Anilist. **This means Hisha cannot automatically identify a show name. You should do this manually or get it beforehand.**

Calling `search()` will request Hisha to make up to (3) calls to Anilist's GraphQL API to attempt to find the show's information. In any case, a HishaInfo object will be returned. It contains various properties:

| Property | Default Value |
| -- | -- |
| id | -1 |
| idMal | -1 |
| idKitsu | -1 |
| episodes | -1 |
| duration | -1 |
| popularity | -1 |
| averageScore | -1 |
| bannerImage | "" |
| coverImage | "" |
| title | "Unknown" |
| title_userPreferred | "Unknown" |
| title_native | "Unknown" |
| title_english | "Unknown" |
| title_romaji | "Unknown" |
| startYear | -1 |
| endYear | -1 |

Note: "title" and "title_userPreferred" are the same property

---

[aleytia](https://github.com/Aleytia) | [best.moe](https://best.moe) | 2019