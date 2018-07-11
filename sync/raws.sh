#!/bin/bash
#/media/9da3/rocalyte/bin/rclone2 copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/.temp-rein/ carmilla-kan:Anime/Raw/ -v &
/media/9da3/rocalyte/bin/rclone2 copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/.temp-rein/ carmilla-tw2:"Raw Shows - Anime (EXPERIMENTAL)" -v &
/media/9da3/rocalyte/bin/rclone2 copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/.temp-rein/ carmilla-wizo:"Raw Shows" -v &

wait
