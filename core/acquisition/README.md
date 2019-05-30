# Acquistion

## Introduction

Unit 1, Acquistion (*Ichika*, 一花) handles processing new file uploads. It:
- Uses inotify to watch a folder for new uploads (see: [rutorrent:autotools](https://github.com/Novik/ruTorrent/wiki/PluginAutotools))
- Uses [anitopy](https://github.com/igorcmoura/anitopy) to rename episodes to a "cleaner" format
- Optionally uses Hisha to find the show name of the new file, if not provided
- Uploads new files to one or more destinations with [rclone](https://rclone.org/)

The entire process occurs in a temporary folder with a hardlinked copy of the file. Once completed, the **original file is deleted, so users should trigger the Acquisition pipeline with a copy of the file**. 

*This is by far the most complicated setup of all the units. Feel free to shoot me an email for clarifications.*

## Setup and Usage

  1. [Configuring ruTorrent](#configuring-rutorrent)
  2. [Configuring Upload Destinations](#configuring-upload-destinations)
  3. [Configuring Endpoints](#configuring-endpoints)
  4. [Configuring System Properties](#configuring-system-properties)
  5. [Starting Acquisition](#starting-acquisition)


Acquisition can be run either as an interactive program (e.g., in tmux), or as a Docker container. There are no differences in either use case, but Docker containers will require a build and a change to a mounted volume. 

*ruTorrent configuration is included in this README, but it is not necessary for Acquisition. This is a rundown of how to configure ruTorrent to automate new downloads into Acquistion.*

### Configuring ruTorrent

Acquisition is intended to be a complement to ruTorrent and the Autotools plugin. There are plans in the future to make Acquisition executable with command-line arguments, too. 

Note: **Acquisition configurations are in [config.yml](./app/config.yml)**

Please first read [Autotools Documentation](https://github.com/Novik/ruTorrent/wiki/PluginAutotools). The rest of this writeup will make much more sense. Autotools's Autoremove is REQUIRED if using ruTorrent.

There are several paths that are of importance. They are:
- `rutorrent.rc directory path`: This is the folder Autotools will copy new downloads from (the entire new download file structure is copied). This is not an Acquisition config.
- `Autotools folder`: This folder is where new **completed** downloads are moved to. This is the "path to finished downloads" in Autotools.
- `watch-folder`: A folder settable in config.yml (under the same name) where Acquisition where watch for new files. This should be the same *folder reference* as `Autotools folder`. **If Acquisition is run in Docker, set this folder in the `start.sh` script's host volume instead of in the config.**. It will be automatically set in a future update.

*Folder reference means the same folder on the hard drive should be pointed at in both `Autotools folder` and `watch-folder`. These are not necessarily the exact same path - set accordingly if Docker volumes are being used.*

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

Izumi uses rclone to upload new files. Upload destinations can be specified as a list in uploading/upload-destinations.
Include the full path of the rclone destination you would like to upload new files to. (It does not matter if your destination ends with a `/` or not).
You can also specify an "airing folder name" that gets append to the end of all the upload-destinations.

**If you want to have new episodes mass-distributed to various destinations, there is also a Distributor module to handle this**. This can also be handy if you want to domain-separate uploader access, or have multiple distributors.

For example, if a rclone destination is set to `dest:Anime` with `airing-folder-name="Airing"`, then new episodes will be uploaded to:
```
dest:Anime/Airing/$SHOW_NAME/$EPISODE

# Example Result:
mega:Anime/Airing/5-Toubun no Hanayome/5-Toubun no Hanayome - 01 [1080p].mkv
```
The folder that represents the show is added automatically (or specified above). There is no way to turn this off.

### Configuring Endpoints

*Familiarity with YAML syntax is required for this section.*

Distributor, Encoder, and Notification all are activated using JSON post requests made from Acquisition (or each other). The JSON payload is identical in every request, and has the following form:

```
{
	"show": "SHOW_NAME",
	"episode": "EPISODE_NAME",
	"filesize": 99999999,
	"sub": "hardsub"
}
```

`filesize` is the size of the episode in bytes, and `sub` is either "hardsub" or "softsub". In Acquisition's case, "softsub" is set (as uploads are presumed to be MKV files with soft subs).

In [config.yml](./app/config.yml), under the `endpoints` key, there are separate sections for encoders, notifiers, and distributors. Note that these groupings are more a formality - the payload sent is the same. 

There are two types of request "attempts", "always" and "sequential" (as seen in config.):
  - Every provided endpoint in `always` will *always* be sent. 
  - In `sequential`, for each group (dict) provided, the endpoints will be tested in order provided until one is successful (or none are).

Each "endpoint" is a dict-style object with two keys. The `url` key is required, and is the URL that the JSON payload will be sent to. The `auth` key is optional (shown in the config), which is an optional "authorization" key that can be sent as a header. (Encoder, Distributor, and Notifications optionally support an `auth.yml` file to authorize incoming requests; this `auth` key is for exactly that).

### Configuring System Properties

System properties are various application properties that Izumi uses.

  - `name`: For logging purposes, this will be the "name" that appears for the running Acquisition module.
  - `delimiter`: Acquisition makes use of inotify-tools's folder watching ability to detect new episodes. This delimiter is used to separate provided arguments. Avoid using characters that might appear in show names (e.g., apostrophes).
  - `verbose`: Whether or not to print more verbose logging output.
  - `logging/logfmt`: Logging message format to output. See Python's logging documentation for more info.
  - `logging/datefmt`: Date output format for logging messages. See Python's logging documentation for more info.

### Starting Acquisition

Make sure all other configurations in this README have been followed, or else Acquisition won't work right.

#### Interactive/Tmux/Screen

To start Acquisition, run the `watch.sh` script inside the app/ folder. This will initialize inotify-tools to watch your configured folder for new downloads. Any new files moved into the watched folder will be processed.

#### Docker

Run `build.sh` to create a Docker image that has your current config baked in. (Changes to config.yml will need new builds). Then, run `start.sh` to start the Docker container. By default, the container will be called `izumi-acquisition`.