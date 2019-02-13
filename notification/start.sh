#!/bin/bash

docker run \
	-p "18000:80" \
	--name "izumi-notifications" \
	-v "$(pwd)/conf:/conf" \
	--restart always \
	${1:-izumi_notifications}
