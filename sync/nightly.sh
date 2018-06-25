#!/bin/bash

NC="\033[0m"
CYAN="\033[1;36m"
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"


function update {

	echo
	echo -e "Synchronizing the state of ${CYAN}$2${NC}..."
	echo
	
	echo -e "${YELLOW}(1/4)${NC}: Synchronizing ${YELLOW}Currently Airing${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Currently Airing" $3:"Currently Airing Shows" -v
	echo -e "${YELLOW}(2/4)${NC}: Synchronizing ${YELLOW}Currently Airing [Hardsub]${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Currently Airing [Hardsub]" $3:"Currently Airing Shows [Hardsub]" -v
	echo -e "${YELLOW}(3/4)${NC}: Synchronizing ${YELLOW}Premiered${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Premiered" $3:"Premiered Shows" -v
	echo -e "${YELLOW}(4/4)${NC}: Synchronizing ${YELLOW}Premiered [Hardsub]${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Premiered [Hardsub]" $3:"Premiered Shows [Hardsub]" -v

	echo
	echo -e "${GREEN}Completed ${NC}synchronizing ${CYAN}$2${NC}."
	echo

}

# List of dests to update, always make arg-1 "carmilla-kan"
update "carmilla-kan" "Triton Weeaboos" "carmilla-tw"
