#!/bin/bash

DOCKER_PORT="$(grep '^port = ' conf/izumi.toml | awk -F '= ' '{print $2}')"
DOCKER_NAME="$(grep '^name = ' conf/izumi.toml | awk -F '"' '{print $2}')"

echo "Starting Izumi Redis in Docker, mapping to port $DOCKER_PORT"
echo "Docker container name is '$DOCKER_NAME'"

docker run -d \
    -v $(pwd)/conf/redis.conf:/usr/local/etc/redis/redis.conf \
    -p "$DOCKER_PORT:6379" \
    --name "$DOCKER_NAME" \
    -l "traefik.enable=false" \
    redis:5.0.7-alpine redis-server /usr/local/etc/redis/redis.conf

docker logs -f "$DOCKER_NAME"
