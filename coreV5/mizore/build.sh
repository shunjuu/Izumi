#!/bin/bash

function izumi {
    IMAGE_NAME="$(grep '^image_name = ' conf/izumi.toml | awk -F '"' '{print $2}')"
    echo "Building Izumi Applet server with image name: $IMAGE_NAME"

    docker build -f "docker/Izumi.Dockerfile" -t "$IMAGE_NAME" .
}

function encode {
    IMAGE_NAME="$(grep '^image_name = ' conf/encoder.toml | awk -F '"' '{print $2}')"
    echo "Building Izumi encoding worker with image name: $IMAGE_NAME"
    docker build \
        -f "docker/Encode.Dockerfile" \
        -t "$IMAGE_NAME" \
        --build-arg WORKER_NAME="$(whoami)@$(hostname):$(date +%Y%m%d.%H%M)" \
        .
}

function notify {
    IMAGE_NAME="$(grep '^image_name = ' conf/notifier.toml | awk -F '"' '{print $2}')"
    echo "Building Izumi notifier worker with image name: $IMAGE_NAME"
    docker build \
        -f "docker/Notify.Dockerfile" \
        -t "$IMAGE_NAME" \
        --build-arg WORKER_NAME="$(whoami)@$(hostname):$(date +%Y%m%d.%H%M)" \
        .
}

function distribute {
    IMAGE_NAME="$(grep '^image_name = ' conf/distributor.toml | awk -F '"' '{print $2}')"
    echo "Building Izumi distributor worker with image name: $IMAGE_NAME"
    docker build \
        -f "docker/Distribute.Dockerfile" \
        -t "$IMAGE_NAME" \
        --build-arg WORKER_NAME="$(whoami)@$(hostname):$(date +%Y%m%d.%H%M)" \
        .
}

function worker {
    IMAGE_NAME="$(grep '^image_name = ' conf/worker.toml | awk -F '"' '{print $2}')"
    echo "Building Izumi worker with image name: $IMAGE_NAME"
    docker build \
        -f "docker/Worker.Dockerfile" \
        -t "$IMAGE_NAME" \
        --build-arg WORKER_NAME="$(whoami)@$(hostname):$(date +%Y%m%d.%H%M)" \
        .
}

function helper {
    echo "Run the script with one of the following args: "
    echo "izumi || i || encode || e || notify || n || work || w"
}

case "$1" in

    "izumi"|"i")
        izumi
        ;;

    "encode"|"e"|"encoder")
        encode
        ;;

    "notify"|"notifier"|"n")
        notify
        ;;

    "distribute"|"distributor"|"d")
        distribute
        ;;

    "worker"|"work"|"w")
        worker
        ;;

    "help"|"h")
        helper
        ;;

    *)
        helper
        ;;

esac