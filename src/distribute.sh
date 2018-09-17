#!/bin/bash

# Distribution is pretty straightforward. In conf.sync.mp4-distribution.distribution, we have multiple lists.
# Each list.0 is the source, and every element after is a destination to sync to.
# Assume that we are not blocked from syncing.

NC="\033[0m"
CYAN="\033[1;36m"
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"

DIST_PATH="sync.mp4-distribution.distribution"


# Get the current working directory
curr_dir=$(echo $PWD)

# Get yq
yq=$(eval realpath "$curr_dir/bin/yq")

# Get the config
config=$(eval realpath "config.yml")

# This is the number of elements in sync.mp4-distribution.distribution.
# "- -.*" is a regex that returns all of the top level elements, as it is a list of lists
TOTAL_DISTRIBUTION_COUNT=$(eval "$yq" read "$config" "$DIST_PATH" | grep -e "- -.*" | wc -l)

echo -e "${CYAN}INFO:${NC} Detected ${CYAN}$TOTAL_DISTRIBUTION_COUNT${NC} distribution configurations."
echo

for d in $(seq 0 $(($TOTAL_DISTRIBUTION_COUNT-1)));
do
	# Get the src location, which is idx 0 of the current distribution
	# Get the number of destinations, this is one less than the total count
	# idx 0 is the source
	CURR_DIST_DEST_COUNT=$(($(eval "$yq" read "$config" "$DIST_PATH.$d" | wc -l) - 1))
	CURR_DIST_SRC=$(eval "$yq" read "$config" "$DIST_PATH.$d.0")
	echo -e "${CYAN}INFO: ${NC}Distribution config ${CYAN}#$(($d+1))${NC}, sourcing from ${CYAN}$CURR_DIST_SRC${NC}."
	echo -e "${CYAN}INFO: ${NC}There are ${CYAN}$CURR_DIST_DEST_COUNT${NC} total destinations for this config."

	# Run a file synchronization in paralle, and wait for it to cmoplete
	for i in $(seq 1 $CURR_DIST_DEST_COUNT);
	do
		CURR_DEST_TO_SYNC=$(eval "$yq" read "$config" "$DIST_PATH.$d.$i")
		echo -e "${GREEN}NOTICE: ${NC}Copying from ${CYAN}$CURR_DIST_SRC${NC} to ${CYAN}$CURR_DEST_TO_SYNC${NC}."
		rclone copy "$CURR_DIST_SRC" "$CURR_DEST_TO_SYNC" -v &
	done

	wait
	echo

done

echo -e "${GREEN}NOTICE: ${NC}Completed MP4 distribution."

