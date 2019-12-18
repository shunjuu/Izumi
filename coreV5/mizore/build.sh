#!/bin/bash

function izumi {
    IMAGE_NAME="$(grep '^image_name = ' conf/izumi.toml | awk -F '"' '{print $2}')"
    echo "Building Izumi Applet server with image name: $IMAGE_NAME"

    docker build -f "docker/Izumi.Dockerfile" -t "$IMAGE_NAME" .
}

function encode {
    echo "Building Izumi encoding worker"
    docker build \
        -f "docker/Encode.Dockerfile" \
        -t "izumi/v5/encoder" \
        --build-arg WORKER_NAME="$(whoami)@$(hostname):$(date +%Y%m%d.%H%M)" \
        .
}

function helper {
    echo "Run the script with one of the following args: "
    echo "izumi || i || encode || e"
}

case "$1" in

    "izumi"|"i")
        izumi
        ;;
    
    "encode"|"e"|"encoder")
        encode
        ;;
    
    "help"|"h")
        helper
        ;;
    
    *)
        helper
        ;;

esac