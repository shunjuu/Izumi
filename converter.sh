#!/bin/bash

inotifywait -m -r -c \
	/home/izumi/izumi/NyaaV2 \
	-e create |
	while read line; do
#		echo $line
#		(python3 new_file.py "$line") &
		python3 new_file.py "$line"
	done
