#!/bin/bash
echo "Syncing Triton Weeaboos..."
/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/NyaaKV/ carmilla-tw:"Currently Airing Shows" -v
echo "Done"
echo "Syncing Triton Weeaboos 2..."
/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/NyaaKV/ carmilla-tw2:"Currently Airing Shows" -v
echo "Done"
echo "Syncing Toshokan..."
/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/NyaaKV/ carmilla-kan:Anime/"Currently Airing" -v
echo "Done"
echo "Syncing to Weebrary..."
/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/NyaaKV/ carmilla-wizo:"Currently Airing Shows" -v
echo "Done"

