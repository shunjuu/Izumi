# Akari

## Introduction

Akari (明かり, lit. "light"), is a wrapper around Jikan.moe to obtain a given user's list of anime that they are either watching or planning to watch. 
It accepts a username and a show name or show ID, and then returns a Boolean indicating whether or not the user is watching that show.

This module was written in part considering the interaction between the requests library and Jikan.moe's API can be unstable with a high rate of failure. Akari is able to retry multiple times for a successful return, and contains all errors within itself. (Retries are spaced by 5 seconds each).

## Usage

Akari contains two primary public methods that both return a Boolean:
- `def is_user_watching_names(self, user, show_name, times=5)`
- `def is_user_watching_id(self, user, malID, times=5)`

`is_user_watching_names` accepts two required parameters and one optional parameter:
- `user` (required): A String representing a username on MyAnimeList
- `show_name` (required): A String representing a show to check for
- `times` (optional): How many times Akari should attempt to contact jikan.moe whenever (until one attempt is successful).

`is_user_watching_id` accepts two required parameters and one optional parameter:
- `user` (required): A String representing a username on MyAnimeList
- `id` (required): A String or an int representing the show ID (mal_id) of a show. Useful for automation.
- `times` (optional): How many times Akari should attempt to contact jikan.moe whenever (until one attempt is successful).

---

[aleytia](https://github.com/Aleytia) | [best.moe](https://best.moe) | 2019