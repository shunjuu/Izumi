#!/bin/bash

NC="\033[0m"
CYAN="\033[1;36m"
RED="\033[0;31m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"

function update_kan_parallel {
	
	echo
	echo -e "Synchronizing the state of ${CYAN}$2${NC}..."
	echo

	echo -e "${YELLOW}(1/4)${NC},${YELLOW}(2/4)${NC}: Synchronizing [${CYAN}$2${NC}] ${YELLOW}Currently Airing${NC} and ${YELLOW}Premiered${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Currently Airing" $3:"Currently Airing Shows" -v &
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Premiered" $3:"Premiered Shows" -v &
	wait

	echo -e "${YELLOW}(3/4)${NC},${YELLOW}(4/4)${NC}: Synchronizing [${CYAN}$2${NC}] ${YELLOW}Currently Airing [Hardsub]${NC} and ${YELLOW}Premiered [Hardsub]${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Currently Airing [Hardsub]" $3:"Currently Airing Shows [Hardsub]" -v &
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Premiered [Hardsub]" $3:"Premiered Shows [Hardsub]" -v &
	wait

	echo
	echo -e "${GREEN}Completed ${NC}synchronizing ${CYAN}$2${NC}."
	echo
}

function update_gen_parallel {
	
	echo
	echo -e "Synchronizing the state of ${CYAN}$2${NC}..."
	echo

	echo -e "${YELLOW}(1/4)${NC},${YELLOW}(2/4)${NC}: Synchronizing [${CYAN}$2${NC}] ${YELLOW}Currently Airing Shows${NC} and ${YELLOW}Premiered Shows${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:"Currently Airing Shows" $3:"Currently Airing Shows" -v &
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:"Premiered Shows" $3:"Premiered Shows" -v &
	wait

	echo -e "${YELLOW}(3/4)${NC},${YELLOW}(4/4)${NC}: Synchronizing [${CYAN}$2${NC}] ${YELLOW}Currently Airing Shows [Hardsub]${NC} and ${YELLOW}Premiered Shows [Hardsub]${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:"Currently Airing Shows [Hardsub]" $3:"Currently Airing Shows [Hardsub]" -v &
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:"Premiered Shows [Hardsub]" $3:"Premiered Shows [Hardsub]" -v &
	wait

	echo
	echo -e "${GREEN}Completed ${NC}synchronizing ${CYAN}$2${NC}."
	echo
}


# List of dests to update, always make arg-1 "carmilla-kan"
update_kan_parallel "carmilla-kan" "Triton Weeaboos v2" "carmilla-tw2"

# Args: source dir, display name of dest dir, dest dir
update_gen_parallel "carmilla-tw2" "Weebrary Mirror" "carmilla-wizo"

