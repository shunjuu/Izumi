# Acquistion

## Introduction

Unit 1, Acquistion (*Ichika*, 一花) handles processing new file uploads. It:
- Uses inotify to watch a folder for new uploads (see: [rutorrent:autotools](https://github.com/Novik/ruTorrent/wiki/PluginAutotools))
- Uses [anitopy](https://github.com/igorcmoura/anitopy) to rename episodes to a "cleaner" format
- Optionally uses Hisha to find the show name of the new file, if not provided
- Uploads new files to one or more destinations with [rclone](https://rclone.org/)

The entire process occurs in a temporary folder with a hardlinked copy of the file. Once completed, the **original file is deleted, so users should trigger the Acquisition pipeline with a copy of the file**. 

## Setup and Usage

### Configuring ruTorrent

Acquisition can be run either as an interactive program (e.g., in tmux), or as a Docker container. There are no differences in either use case, but Docker containers will require a build and a change to a mounted volume.

Acquisition is intended to be a complement to ruTorrent and the Autotools plugin. There are plans in the future to make Acquisition executable with command-line arguments, too. 

Note: **All configurations are in [config.yml](./app/config.yml)**

Please first read [Autotools Documentation](https://github.com/Novik/ruTorrent/wiki/PluginAutotools). The rest of this writeup will make much more sense.

There are several paths that are of importance. They are:
- `rutorrent.rc directory path`: This is the folder Autotools will copy new downloads from (the entire new download file structure is copied).
- `Autotools folder`: This folder is where new **completed** downloads are moved to. 
- `watch-folder`: A folder in the configuration where Acquisition where watch for new files. This should be the same as `Autotools folder`.

When saving new files (manually or in RSS), you should save them to the `rutorrent.rc directory path`. For example purposes, let us assume this path is `/home/rutorrent/incompleted/`, and that the `Autotools folder` is `/home/rutorrent/completed`.
Then, in a standard download sequence, the episode would first be written to:
```
/home/rutorrent/incompleted/Episode.mkv
```
Upon completion, Autotools will move it to:
```
/home/rutorrent/completed/Episode.mkv
```
And at this point, Acquisition will detect the new episode. However, if possible, users should also pre-specify the show name of the new episode (as Hisha is not yet stable). It can be done by appending a folder (that is the show name) to the end of the `rutorrent.rc directory path` and saving the new episode inside that folder.

For example, if we want to pre-specify that this episode is from 5-Toubun no Hanayome, save the new file (or in your RSS, specify the download path as):
```
/home/rutorrent/incompleted/5-Toubun no Hanayome/
```
Acquisition will automatically detect any episodes under this path to be from the show "5-Toubun no Hanayome". Autotools will respect this file structure, so an example run would be:

```
# A new episode is first written (incomplete download) to:
/home/rutorrent/incompleted/5-Toubun no Hanayome/5-Toubun no Hanayome - 01 [1080p].mkv

# When it's done downloading, Autotools will move it to:
/home/rutorrent/completed/5-Toubun no Hanayome/5-Toubun no Hanayome - 01 [1080p].mkv

# At this point, Acquisition will detect the new episode and start processing it.
```
As you can see above, it is important to note that Autotools copies the entire folder structure to the watch folder. This is critical to passing correct invocation information. 

**All shows uploaded will be automatically organized by its show name**. For RSS feed users, each show should be its own configuration, where each show is a folder appended to the download path. Thus, you would have:

| Show | Save Path | Example Regex |
| --- | --- | --- |
| 5-Toubun no Hanayome | /home/rutorrent/incompleted/5-Toubun no Hanayome | /.*(5-Toubun no Hanayome).*(1080p).*/i |

Alternatively, you can use [Sonarr](https://sonarr.tv/) to handle new downloads, and simply specify their save paths.

### Configuring Upload Destinations

Izumi makes use of rclone to upload new files. Upload destinations can be specified as a list in uploading/upload-destinations.
Include the full path of the rclone destination you would like to upload new files to. (It does not matter if your destination ends with a `/` or not).

**If you want to have new episodes mass-distributed to various destinations, there is also a Distributor module to handle this**. You can also specify an "airing folder name" that gets append to the end of all the upload-destinations.

For example, if a rclone destination is set to `dest:Anime` with `airing-folder-name="Airing"`, then new episodes will be uploaded to:
```
dest:Anime/Airing/$SHOW_NAME/$EPISODE

# Example:
mega:Anime/Airing/5-Toubun no Hanayome/5-Toubun no Hanayome - 01 [1080p].mkv
```
The folder that represents the show is added automatically (or specified above). There is no way to turn this off.

### Configuring Endpoints