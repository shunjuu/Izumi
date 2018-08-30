#!/bin/bash

MP4_CONF_PRIORITY="sync.mp4.priority"
MP4_CONF_REGULAR="sync.mp4.regular"

is_rclone() {
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

	echo "rclone is not running."
	echo
}


# Get the yq executable path
yq=$(eval realpath "bin/yq")

# Get the config file that we'll be using
config=$(eval realpath "config.yml")

# Get the mp4 directory from the config
mp4_dir=$(eval "$yq" read "$config" folders.mp4)
mp4_dir=$(eval realpath "$mp4_dir")
# echo "Scanning from: $mp4_dir"
# echo

# ---- #

# Now that we know the constants, determine how many destinations exist

MP4_UPLOAD_PRIORITY_DESTINATION_COUNT=$(eval "$yq" read "$config" "$MP4_CONF_PRIORITY" | wc -l)
MP4_UPLOAD_REGULAR_DESTINATION_COUNT=$(eval "$yq" read "$config" "$MP4_CONF_REGULAR" | wc -l)

# Make sure rclone isn't running by the user
is_rclone

# run rclone on every single priority destination (no parallel)
for i in $(seq 0 $(($MP4_UPLOAD_PRIORITY_DESTINATION_COUNT-1)));
do
	p_dest=$(eval "$yq" read "$config" "$MP4_CONF_PRIORITY.$i")
	#echo "rclone copy "$mp4_dir" "$p_dest" -v"
	rclone copy "$mp4_dir" "$p_dest" -v
done

echo

# run rclone on every single regular destination (parallel)
for i in $(seq 0 $(($MP4_UPLOAD_REGULAR_DESTINATION_COUNT-1)));
do
	r_dest=$(eval "$yq" read "$config" "$MP4_CONF_REGULAR.$i")
	#the echo "rclone copy "$mp4_dir" "$r_dest" -v &"
	rclone copy "$mp4_dir" "$r_dest" -v &
done

wait
