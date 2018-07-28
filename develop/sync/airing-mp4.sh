#!/bin/bash
echo "Syncing Triton Weeaboos..."
/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/Nyaa4/ carmilla-tw:"Currently Airing Shows [Hardsub]" -v
echo "Done"
echo "Syncing Triton Weeaboos 2..."
/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/Nyaa4/ carmilla-tw2:"Currently Airing Shows [Hardsub]" -v
echo "Done"
echo "Syncing Toshokan..."
/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/Nyaa4/ carmilla-kan:Anime/"Currently Airing [Hardsub]" -v
echo "Done"
echo "Syncing to Weebrary..."
/media/9da3/rocalyte/bin/rclone copy /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/Nyaa4/ carmilla-wizo:"Currently Airing Shows [Hardsub]" -v
echo "Done"

