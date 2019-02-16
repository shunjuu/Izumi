#!/bin/bash

docker run -d \
	--name "izumi-acquisition" \
	-v "$(pwd)/conf:/conf" \
	-v "$(pwd)/watch:/watch" \
	--restart always \
	${1:-izumi_acquisition}
