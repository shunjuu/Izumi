# Kishi

## Introduction

Kishi (騎士, lit. "knight") is a wrapper around Anilist's GraphQL API to obtain a given user's list of anime that they are watching, planning to watch, or have on hold.
It accepts a username and a show name or a show ID, both presumed to already be matching Anilist's equivalents. 

## Usage 

Kishi contains two primary public methods that both return a Boolean:
- `def is_user_watching_names(self, user, show_name)`
- `def is_user_watching_id(self, user, show_id)`

`is_user_watching_names` accepts two required parameters:
- `user` (required): A String representing a username on Anilist
- `show_name` (required): A String representing a show to check for

`is_user_watching_id` accepts two required parameters:
- `user` (required): A String representing a username on Anilist:
- `show_id` (required): A String or an int representing the show ID (anilist_id) of a show. Useful for automation.

---

[aleytia](https://github.com/Aleytia) | [best.moe](https://best.moe) | 2019