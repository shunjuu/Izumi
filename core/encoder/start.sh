#!/bin/bash

docker run -d \
	-p "127.0.0.1:17000:80" \
	--name "izumi-encoder" \
	-e DOCKER='true' \
	-l "traefik.enable=false" \
	--restart always \
	${1:-izumi_encoder}
