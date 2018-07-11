#!/bin/bash
SUBS="subtitles='""$2""'"
THREADS=$6

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

}

ffmpeg -i "$1" -vf "$SUBS" -c:a copy -threads $THREADS -y -nostdin "$3"

newsize=$(wc -c < "$3")
if [[ "$newsize" == "0" ]]; then
	echo "Error with 8-bit ffmpeg, trying 10-bit..."
	ffmpeg-10bit -i "$1" -vf "$SUBS" -c:a copy -threads $THREADS -y -nostdin "$3"
fi

is_rclone

mkdir -p "$5"
mv "$3" "$4"
