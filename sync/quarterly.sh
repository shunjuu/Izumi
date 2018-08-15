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

	../util/is_rclone.sh

	echo -e "${YELLOW}(1/2)${NC},${YELLOW}(2/2)${NC}: Synchronizing [${CYAN}$2${NC}] ${YELLOW}Airing${NC} and ${YELLOW}Airing [Hardsub]${NC}..."
	echo
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Airing" $3:"Airing" -v &
	/media/9da3/rocalyte/bin/rclone --config="/media/9da3/rocalyte/.config/rclone/rclone.conf" sync $1:Anime/"Airing [Hardsub]" $3:"Airing [Hardsub]" -v &
	wait

	echo
	echo -e "${GREEN}Completed ${NC}synchronizing ${CYAN}$2${NC}."
	echo
}



# List of dests to update, always make arg-1 "carmilla-kan"
# Args: source dir, display name of dest dir, dest dir
update_kan_parallel "sanka-kan" "TW Mirror" "carmilla-wizo"
#update_gen_parallel "carmilla-wizo" "Weebrary" "weebrary"
