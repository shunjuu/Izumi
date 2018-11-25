#!/bin/bash

# First, we want to check if ./watch.sh is active and running

if [[ $(/usr/bin/pgrep -u $(whoami) watch.sh) ]]; then
	# Watch is running, so we do nothing
	echo "Watch is running, doing nothing..."
else
	# Watch isn't running, so we need to restart the tmux session
	echo "Watch isn't running, starting new session..."
	sleep 2

	# Create a new session
	/usr/bin/tmux new -s watch -d

fi
