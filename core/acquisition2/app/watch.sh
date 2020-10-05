#!/bin/bash

# Clear the terminal
clear

if [[ -z "${DOCKER}" ]]; then

	# Get the current working directory in absolute path
	curr_dir=$(echo $PWD)
	yq="$curr_dir/bin/yq"

	# Get the directory to watch
	watch_dir=$(eval "$yq" read config.yml watch-folder)
	# watch_dir needs to be an absolute path, or else inotify
	# will pass in the wrong path
	watch_dir=$(realpath "$watch_dir")

	# we also need to fetch the delimiter string for inotify
	delim=$(eval "$yq" read config.yml system.delimiter)

	# get the location of acquisition
	acquisition="acquisition.py"

else
	# Docker is being used - set all variables to docker defaults
	yq="/src/bin/yq"
	watch_dir="/watch"
	delim=$(eval "$yq" read /src/config.yml system.delimiter)
	acquisition="/src/acquisition.py"

fi

# we also need to fetch the delimiter string for inotify
# delim=$(eval "$yq" read /conf/config.yml system.delimiter)

echo "Now watching: $watch_dir"
echo

inotifywait -m -r --format "%w$delim%e$delim%f" \
    "$watch_dir" \
    -e create -e move |
    while read line; do
        python3 "$acquisition" "$line"
    done
