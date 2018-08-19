#!/bin/bash
# Delete any episode that is a week old, approx.
/media/9da3/rocalyte/bin/rclone2 --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" delete --min-age 167h mega:Lagniappe -v
# Delete the empty folders too
/media/9da3/rocalyte/bin/rclone2 --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" rmdirs mega:Lagniappe -v
