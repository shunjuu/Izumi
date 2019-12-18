#!/bin/bash

docker run -d \
    -v $(pwd)/conf/redis.conf:/usr/local/etc/redis/redis.conf \
    -p 6379:6379 \
    --name redisdev \
    redis redis-server /usr/local/etc/redis/redis.conf