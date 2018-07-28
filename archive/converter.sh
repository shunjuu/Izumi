#!/bin/bash

inotifywait -m -r -c \
	/media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/.Nyaa \
	-e create |
	while read line; do
		(python3 convert_new.py "$line") &
	done
