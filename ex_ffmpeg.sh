#!/bin/bash
SUBS="subtitles='""$3""'"
echo "$SUBS"

#$1 -i "$2" -vf "$SUBS" "$4"
$1 -i "$2" -vf "$SUBS" -threads 12 "$4"

/bin/bash /media/9da3/rocalyte/private/scripts/clean/is_rclone.sh

mkdir "$6"
mv "$4" "$5"

