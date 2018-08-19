#!/bin/bash

inotifywait -m -r -c \
	/media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/.NyaaV2 \
	-e create |
	while read line; do
#		echo $line
#		(python3 new_file.py "$line") &
		python3 new_file.py "$line"
	done
