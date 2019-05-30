# Izumi

## Introduction
Izumi (泉), meaning "spring/fountain" in Japanese, is a distributed automation infrastructure framework for processing Japanese video files. It is a collection of various application units and shared modules that collectively handle a complete "streaming site"-like experience, primarily for anime.


## The Five Units
Izumi is primarily split into five "primary" units, that each handle a different major aspect of the system. They are nicknamed after the quintuplets from Negi Haruba's 五等分の花嫁 series. Each individual module can be run in an interactive shell (or "daemonized" in tmux), or can be built and run as Docker containers. More documentation can be found in each unit's respective folder.

#### **Acquisition** (Unit 1)

Acquisition (nicknamed as 一花) handles obtaining new anime episodes, determining various information about the episodes, and uploading the files into a storage medium of choice. It is designed to attach to rTorrent/ruTorrent's Autotools plugin, and has the functionality to automatically detect the show names of the episodes as well as automatically organize episodes by their shows. 

#### **Encoder** (Unit 2)

Encoder (nicknamed as 二乃) handles encoding new episodes to other formats, using ffmpeg as a backend. Currently, the only enabled encoding sub-module within Encoder will "hardsub" ("burn in subtitles") new videos into a H264 MPEG file. 

#### **Notifications** (Unit 3)

Notifications/Notifier (nicknamed as 三玖) sends new episode upload notifications to end-users. It (and Izumi) uses the [Hisha](./modules/hisha/README.md) module to fetch episode and show information. Currently, Notifications can be sent as Discord webhooks, with the following planned/in progress: Facebook Messenger, Line, and SMS. Notifications can also be selectively sent based on an Anilist and/or MyAnimeList profile's Watching, Paused/Hold, and Plan to Watch lists.

#### **Distribution** (Unit 4)
Distribution/Distributor (nicknamed as 四葉) handles taking new uploads from Acquisition and/or Encoder and distributes them to various storage locations. This unit is intended to remove the necessity of having Acquisition/Encoder handle all the uploading, or for cases where certain servers may have better bandwdith, etc.

#### **Tools** (Unit 5)
Tools (nicknamed as 五月), unlike the other units, does not run as a daemonized service. It is an interactive program that allows service administrators to easily manage shows in their storage locations. It currently supports 6 operations:

  1. *Move*: Move shows from 'Airing' to 'Premiered' folders. Optionally can append the native Japanese name.
  2. *Rmdir*: Removes empty directories from any location.
  3. *Rename Episodes*: Renames episodes in a folder to a "cleaner" style (Acquisition automatically does this).
  4. *Subdirectory*: Moves a show's episodes into a subdirectory of itself (e.g., if a show has multiple seasons)
  5. *Rename Folder*: Renames a single folder. Useful to change a show's name.
  6. *Delete*: Deletes a show.

## Shared Modules

There are also additional shared modules that various units may use. More documentation can be found in each module's respective folder.

#### Akari
[Akari](modules/akari/README.md) (明かり) is a wrapper around Jikan.moe to obtain a user's MyAnimeList list of anime they are watching, planning to watch, or have on hold.

#### Hisha
[Hisha](modules/hisha/README.md) (飛車) is a utility module to fetch \[airing\] anime show information from Anilist's GraphQL API.

#### Hisoka
[Hisoka](https://github.com/Aleytia/Hisoka) (密か) is a shell script that can deploy 3 Docker containers: A PIA container, a rTorrent/ruTorrent container (that connects through the PIA container), and a Nginx container (to expose the ruTorrent WebUI to the host machine).

#### Kishi
[Kishi](modules/kishi/README.md) (騎士) is a wrapper around Anilist's GraphQL API to obtain a user's Anilist list of anime they are watching, planning to watch, or have on hold.


## Notes
Documentation is currently incomplete. It is being worked on, but is expected to take a while before everything is fully documented. 

Please feel free to contribute. Pull requests will be reviewed and merged as applicable.

---

© aleytia | [best.moe](best.moe) | rocia @ freenode
