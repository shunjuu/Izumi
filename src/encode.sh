#!/bin/bash

# Get the current working directory
curr_dir=$(echo $PWD)

# Get yq
yq=$(eval realpath "$curr_dir/bin/yq")

# Get the config file
config=$(eval realpath "config.yml")

# Get the number of threads to use
THREADS=$(eval "$yq" read "$config" ffmpeg.threads)

# Get the ffmpeg args
ffmpeg8=$(eval realpath "$curr_dir/bin/ffmpeg")
ffmpeg10=$(eval realpath "$curr_dir/bin/ffmpeg-10bit")

# Take the passed in args and store them
tempfile="$1"
hardsubfile="$2"

echo "$ffmpeg8"
echo "$ffmpeg10"
echo
echo "$tempfile"
echo "$hardsubfile"

# Run standard 8-bit color encoding
"$ffmpeg8" -i "$tempfile" -vf subtitles="$tempfile" -c:a copy -threads $THREADS -y -nostdin -strict -2 "$hardsubfile"

# If 8-bit fails, the new video file may be 10-bit encoded
newsize=$(wc -c < "$hardsubfile")
if [[ "$newsize" == "0" ]]; then
		echo "An error was detected using 8-bit encoding. Trying with 10-bit..."
		"$ffmpeg10" -i "$tempfile" -vf subtitles="$tempfile" -c:a copy -threads $THREADS -y -nostdin -strict -2 "$hardsubfile"
fi

 
