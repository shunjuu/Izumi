#!/bin/bash

clear
# Get the current working directory in absolute path
curr_dir=$(echo $PWD)
yq="$curr_dir/bin/yq"

# Get the directory to watch
watch_dir=$(eval "$yq" read config.yml folders.watch)

# watch_dir needs to be an absolute path, or else inotify
# will pass in the wrong path
watch_dir=$(realpath "$watch_dir")

# we also need to fetch the delimiter string for inotify
delim=$(eval "$yq" read config.yml sys.delimiter)

: '
echo "Working directory: $curr_dir"
echo "yq executable: $yq"
echo "watch dir: $watch_dir"
'

echo "Now watching: $watch_dir"

inotifywait -m -r --format "%w$delim%e$delim%f" \
	"$watch_dir" \
	-e create |
	while read line; do
		python3 main.py "$line"
	done


