#!/bin/bash

/bin/echo
if [[ -d /media/9da3/rocalyte/private/rtorrent ]]
then
	/bin/echo -e "\033[31m""Killing all instances of rtorrent""\e[0m"
	/bin/echo
	/bin/kill -9 "$(/usr/bin/screen -ls rtorrent | /bin/sed -rn 's/(.*).rtorrent[^-](.*)/\1/p')" > /dev/null 2>&1
	/usr/bin/screen -wipe > /dev/null 2>&1
	/bin/echo "Restarting rtorrent"
	/bin/echo
	# Test to see if rtorrent is running, if the result is null and the respective lock file exists then delete the lock file. Otherwise do nothing.
	[[ -z "$(/usr/bin/pgrep -fu "$(whoami)" "/opt/rtorrent/current/bin/rtorrent")" && -f /media/9da3/rocalyte/private/rtorrent/work/rtorrent.lock ]] && /bin/rm -f /media/9da3/rocalyte/private/rtorrent/work/rtorrent.lock
	#
	/usr/bin/screen -fa -dmS rtorrent rtorrent
	/bin/sleep 2
	/bin/echo -e "\033[33m""Checking if the process is running:""\e[0m"
	/bin/echo
	/bin/echo "$(ps x | /bin/grep "/opt/rtorrent/current/bin/rtorrent" | /bin/grep -v /bin/grep)"
	/bin/echo
	/bin/echo -e "\033[33m""Checking if the /usr/bin/screen is running""\e[0m"
	/bin/echo
	/bin/echo "$(/usr/bin/screen -ls | /bin/grep rtorrent)"
	/bin/echo
else
	/bin/echo -e "\033[31m""rTorrent is not installed. Nothing to do""\e[0m"
	/bin/echo
fi
