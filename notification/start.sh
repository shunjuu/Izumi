#!/bin/bash

docker run -d \
	-p "17000:80" \
	--name "izumi-notifications" \
	-e DOCKER='true' \
	--restart always \
	${1:-izumi_notifications}
