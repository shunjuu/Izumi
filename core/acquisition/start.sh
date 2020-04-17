#!/bin/bash

docker run -d \
	--name "izumi-acquisition" \
	-v "$(pwd)/watch:/watch" \
	-e DOCKER='true' \
	-l "traefik.enable=false" \
	--restart always \
	${1:-izumi_acquisition}
