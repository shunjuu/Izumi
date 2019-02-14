#!/bin/bash

docker run -d \
	-p "17000:80" \
	--name "izumi-encoder" \
	-v "$(pwd)/conf:/conf" \
	--restart always \
	${1:-izumi_encoder}
