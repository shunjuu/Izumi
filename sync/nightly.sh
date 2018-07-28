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

	echo -e "${YELLOW}(1/4)${NC},${YELLOW}(2/4)${NC}: Synchronizing [${CYAN}$2${NC}] ${YELLOW}Airing${NC} and ${YELLOW}Premiered${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Airing" $3:"Airing" -v &
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Premiered" $3:"Premiered" -v &
	wait

	echo -e "${YELLOW}(3/4)${NC},${YELLOW}(4/4)${NC}: Synchronizing [${CYAN}$2${NC}] ${YELLOW}Airing [Hardsub]${NC} and ${YELLOW}Premiered [Hardsub]${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Airing [Hardsub]" $3:"Airing [Hardsub]" -v &
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Premiered [Hardsub]" $3:"Premiered [Hardsub]" -v &
	wait

	echo
	echo -e "${GREEN}Completed ${NC}synchronizing ${CYAN}$2${NC}."
	echo
}

function update_gen_parallel {
	
	echo
	echo -e "Synchronizing the state of ${CYAN}$2${NC}..."
	echo

	echo -e "${YELLOW}(1/4)${NC},${YELLOW}(2/4)${NC}: Synchronizing [${CYAN}$2${NC}] ${YELLOW}Airing${NC} and ${YELLOW}Premiered${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:"Airing" $3:"Airing" -v &
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:"Premiered" $3:"Premiered" -v &
	wait

	echo -e "${YELLOW}(3/4)${NC},${YELLOW}(4/4)${NC}: Synchronizing [${CYAN}$2${NC}] ${YELLOW}Airing [Hardsub]${NC} and ${YELLOW}Premiered [Hardsub]${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:"Airing [Hardsub]" $3:"Airing [Hardsub]" -v &
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:"Premiered [Hardsub]" $3:"Premiered [Hardsub]" -v &
	wait

	echo
	echo -e "${GREEN}Completed ${NC}synchronizing ${CYAN}$2${NC}."
	echo
}


# List of dests to update, always make arg-1 "carmilla-kan"
# Args: source dir, display name of dest dir, dest dir
update_kan_parallel "sanka-kan" "TW Mirror" "carmilla-wizo"
