#!/bin/bash

docker run -d \
	-p "17000:80" \
	--name "izumi-distributor" \
	-v "$(pwd)/conf:/conf" \
	--restart always \
	${1:-izumi_distributor}
