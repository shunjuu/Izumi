#!/bin/bash
SUBS="subtitles='""$3""'"

#$1 -i "$2" -vf "$SUBS" "$4"
$1 -i "$2" -vf "$SUBS" -c:a copy -threads 12 -y "$4"

newsize=$(wc -c < "$4")
if [[ "$newsize" == "0" ]]; then
	echo "10-bit file detcted."
	ffmpeg-10bit -i "$2" -vf "$SUBS" -c:a copy -threads 12 -y "$4"
fi

#/bin/bash /media/9da3/rocalyte/private/scripts/clean/is_rclone.sh

mkdir -p "$6"
mv "$4" "$5"

