#!/bin/bash

function update_dest {
	echo "Syncing $1..."
	/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/Nyaa4/ $2:"Airing [Hardsub]" -v 
	echo "Done"
}

function update_mp4 {

	echo "Syncing Toshokan..."
	/usr/bin/rclone copy /home/izumi/izumi/Nyaa4/ sanka-kan:"Airing [Hardsub]" -v 
	echo "Done"

	# update_dest "Triton Weeaboos 2" "carmilla-tw2" & 
	# update_dest "Weebrary" "carmilla-wizo" &

	# We can't actually continue until all the syncs are done, so we just want to execute the all at the same time
	# and wait for them to be done
	# wait

}

update_mp4

exit 0

