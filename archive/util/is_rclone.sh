#!/bin/bash

while pgrep -u "$(whoami)" -x "rclone" >/dev/null
do
	echo "Detected rclone is running. Waiting 60 seconds..."
	secs=$((1 * 60))
	while [ $secs -gt 0 ]; do
		echo -ne "Remaining: $secs\033[0K\r"
		sleep 1
		: $((secs--))
	done
done

