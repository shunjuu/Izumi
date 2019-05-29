#!/bin/bash

docker run -d \
	-p "127.0.0.1:17000:80" \
	--name "izumi-distributor" \
	-e DOCKER='true' \
	--restart always \
	${1:-izumi_distributor}
