# Izumi

## Introduction
Izumi (泉), meaning "spring" in Japanese, is an infrastructure management and video processing pipeline tool. It is a collection of five applications that collectively are designed to automatically acquire, organize, distribute, and encode incoming East Asian media files.

Note: Version 4.0 "Tio" is a distributed equivalent of versions 3.x. "Tio" is designed to be run in tmux sessions, while "Tio-Docker" is "Tio" but ported into Docker builds.

## The Five Units
---

### **Acquistion** (Unit 1)
Acquisition handles detecting new files being added into the filesystem.
  
  1. Using `inotify-tools`, Acquisition watches a user-configured folder for new files.
  2. When a new file is detected, Acquisition takes a copy of this file, cleans the filename using [anitopy](https://github.com/igorcmoura/anitopy), and organizes it into a parent folder based on the file's superseries show.
  3. Using [rclone](https://rclone.org/), it then uploads this file to user-configured locations.
  (While this can replicate *Distributor*'s functionality, there is a common use case where it would only be preferable to upload once with Acquisition, and have the rest distributed. See below.)
  4. Acquistion then deletes its temporary files and continues watching the user-configured folder.

### **Encoder** (Unit 2)
Encoder handles encoding files acquired by Acquisition. 
The current module loaded is set to "hardsub" incoming videos, using all default streams.

*Important: Encoder makes use of a worker thread system that starts at step 2. For more information, see below.*

  1. Encoder runs as a Flask webserver listening for new requests. It does not currently use any WSGI setup. It is recommended to run U2 behind a nginx reverse-proxy.
  2. When a new request comes in, the `AuthHandler` class checks if the incoming request contains sufficient credentials to proceed.
  If not, Encoder returns a 401 and exits. If the request is authorized, the request is added into a queue for worker threads to handle.
  3. Next, the next available thread scans the softsub rclone *sources* to find the first source that contains the file.
  Once the file is found, Encoder will download it into a temporary folder.
  Note/TODO: There is currently no handling for when the file is NOT found. 
  4. The file is then encoded with the encoding sub-modules.
  5. The newly-encoded file is then uploaded to all listed upload destinations. 
  Similarly to Acquisition, *Distributor* should be used instead of Encoder's innate uploading functions in some cases. See below.)
  6. Encoder then clears the temporary folder and waits for the next request.

### **Notifications** (Unit 3)
Notifications/Notifier handles sending new file upload notifications to the end-users. Currently, it supports sending rich-embeds on Discord. All anime episode information is fetched from Anilist.

*Important: Notifier makes use of a worker thread system that starts at step 2. For more information, see below.*

  1. Notifier runs as a Flask webserver listening for new requests. It does not currently use any WSGI setup. It is recommended to run U3 behind a nginx reverse-proxy. 
  2. When a new request comes in, the `AuthHandler` class checks if the incoming request contains sufficient credentials to proceed.
  If not, Notifier returns a 401 and exits. If the request is authorized, the request is added into a queue for worker threads to handle.
  3. Next, the next available thread reads the request and fetches the information for each new episode from Anilist.
  4. The information from Anilist is stored into a dict and passed into each notification module. 
  The current list of available modules is:
  [Discord Webhooks]
  5. Each module sends out its own notifications to the end users.
  6. The job is cleared and the thread waits for the next request.

### **Distribution** (Unit 4)
Distribution/Distributor handles taking new uploads from Acquistion and Encoder and distributes them to storage locations. 
While this unit need not exist, it is intended for the use case when the Acquiring and/or Encoding device may not have fast internet or good bandwidth or uploading several times, or when Acquisition and Encoding want a single, centralized distribution pipeline.

*Important: Notifier makes use of a worker thread system that starts at step 2. For more information, see below.*

  1. Distributor runs as a Flask webserver listening for new requests. It does not currently use any WSGI setup. It is recommended to run U4 behind a nginx reverse-proxy. 
  2. When a new request comes in, the `AuthHandler` class checks if the incoming request contains sufficient credentials to proceed.
  If not, Distributor returns a 401 and exits. If the request is authorized, the request is added into a queue for worker threads to handle.
  3. Next, the next available thread reads the request and scans from the respective (softsub/hardsub) source and downloads it as a local file.
  4. Distributor then uploads this file to all the respective (softsub/hardsub) upload destinations using `rclone`.
  5. The file is then deleted locally and the thread cleared for the next request.

### **Tools** (Unit 5)
Unlike the rest of the units, Tools is not intended to run as a daemon, tmux instance, or Docker container. It is a selection of scripts (soon to be updated) that allow easy management of the infrastructure Izumi is currently configured on. It has various tools:

- Move: Move existing shows from the 'Airing' to the 'Premiered' folders, optionally appending the native language in the show folder too.
- Rmdir: Removes empty directories in the system.
- Rename: Takes "messy named" episode (from Sonarr, for example) and renames them to a "clean" format using `anitopy`.
- Season: Moves existing shows into a subdirectory of themselves (generally to sort into seasons).
- Delete: Deletes an existing show from the system.

## Additional Units
---


There are also additional units that are integrated with the system for additional features. Ones currently in development are:

- Kisaragi: Port of [Izumi_DM](https://github.com/Aleytia/Kisaragi) - A Discord bot that can send users personalized notifications for new uploads.

## Worker Threading
---
Worker threading is a technique taken advantage by Izumi to support multiple jobs at once.
In the Python implementation, multiple "worker threads" that do each module's jobs are spawned at boot, continuously reading from a thread-safe Queue and trying to pull requests. 
When a new request is made into the system, this request is processed and added to the Queue, in which the next available thread will process the request when possible. 

## Distributor vs Acquisition/Encoder
---
Units Acquistion and Encoder support specifying multiple rclone endpoint locations. 
This at a glance would seem to nullify any point of having a Distributor unit. 
However, Distributor serves more specific cases in which it may not be preferable to use Acquisition/Encoder to upload everything.

- Case 1: One config, two sources: Distribution can inherently handle both Acquistion and Encoder at the same time. Thus, this can reduce complexity by having Acquistion and Encoder upload to a predetermined location, and let Distributor take it from there.
- Case 2: Acquisition/Encoder are on separate networks, one of which may not have good internet access, or similar.
If an encoder is run at home (to save costs), it's presumable that the home may still not have great upload speeds. Distributor can then be placed on a VPS with a good connection to reduce distribution time and costs.
- Case 3: Domain separation. Because of the semi-decentralized nature of the application (see below), it may be preferable to have some distributors hosted on different machines which have access to storage locations which may not be preferable to have on other machines. 
For example, if two Distributor units are deployed, one distributor can send files to all public-facing servers, while another can upload to private storage locations.

## "Decentralization"
---
While not immediately obvious, the design of the Units allow multiple instances of each one to be deployed. 
This inherently comes with the benefit of being able to configure multiple units for different use cases. Case 3 in the section above is one example.
Multiple units can be set up to support domain separation, or two types of encoders, fallbacks using the Sequential requesters, etc.. 

The possibilities are endless!

---

© aleytia | [best.moe](best.moe) | rocia @ freenode
