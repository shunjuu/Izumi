#!/bin/bash

function update_dest {
	echo "Syncing $1..."
	/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/NyaaKV/ $2:"Currently Airing Shows" -v 
	echo "Done"
}

function update_mkv {

	echo "Syncing Toshokan..."
	/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/NyaaKV/ carmilla-kan:Anime/"Currently Airing" -v 
	echo "Done"

	update_dest "Triton Weeaboos 2" "carmilla-tw2" &
	update_dest "Weebrary" "carmilla-wizo" &

	# We can't actually continue until all the syncs are done, so we just want to execute the all at the same time
	# and wait for them to be done
	wait

}

update_mkv 
exit 0



