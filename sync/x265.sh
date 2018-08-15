#!/bin/bash

/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" copy carmilla-suigen:"Airing [x265]" sanka-kan:Anime/"Airing [x265]" -v
/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" move carmilla-suigen:"Airing [x265]" carmilla-wizo:"Airing [x265]" -v 
/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" rmdirs carmilla-suigen:"Airing [x265]" --leave-root -v
