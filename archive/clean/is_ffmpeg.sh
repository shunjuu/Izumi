#!/bin/bash

if pgrep -u "$(whoami)" -x "ffmpeg" >/dev/null
then
	echo "rclone running detected. Waiting 60 seconds..."
	sleep 60
fi

if pgrep -u "$(whoami)" -x "ffmpeg-10bit" >/dev/null
then
	echo "rclone running detected. Waiting 60 seconds..."
	sleep 60

