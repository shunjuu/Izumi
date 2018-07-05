#!/bin/bash

inotifywait -m -r -c \
	/media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/.NyaaV2 \
	-e create -e move |
	while read line; do
		echo "$line"
#		(python3 convert_new.py "$line") &
	done
