#!/bin/bash

# Get the current working directory
curr_dir=$(echo $PWD)
yq="$curr_dir/bin/yq"

# Get the directory to watch
watch_dir=$(eval yq read config.yml folders.watch)

: '
echo "Working directory: $curr_dir"
echo "yq executable: $yq"
echo "watch dir: $watch_dir"
'

inotifywait -m -r -c \
	"$watch_dir" \
	-e create |
	while read line; do
		python3 main.py "$line"
	done
