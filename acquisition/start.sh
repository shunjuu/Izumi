#!/bin/bash

docker run -d \
	--name "izumi-acquisition" \
	-v "$(pwd)/watch:/watch" \
	-e DOCKER='true' \
	--restart always \
	${1:-izumi_acquisition}
