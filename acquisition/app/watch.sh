#!/bin/bash

# Clear the terminal
clear

# Get the current working directory in absolute path
# curr_dir=$(echo $PWD)
yq="/src/bin/yq"

# Get the directory to watch
# watch_dir=$(eval "$yq" read config.yml watch-folder)
watch_dir="/watch"

# watch_dir needs to be an absolute path, or else inotify
# will pass in the wrong path
# watch_dir=$(realpath "$watch_dir")

# we also need to fetch the delimiter string for inotify
delim=$(eval "$yq" read /conf/config.yml system.delimiter)

echo "Now watching: /watch/"
echo

inotifywait -m -r --format "%w$delim%e$delim%f" \
    "/watch" \
    -e create -e move |
    while read line; do
        python3 /src/acquisition.py "$line"
    done
