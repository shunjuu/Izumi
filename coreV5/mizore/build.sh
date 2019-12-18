#!/bin/bash

function izumi {
    echo "Building Izumi Applet server"
    docker build -f "docker/Izumi.Dockerfile" -t "izumi/v5/applet" .
}

function encode {
    echo "Building Izumi encoding worker"
    docker build \
        -f "docker/Encode.Dockerfile" \
        -t "izumi/v5/encoder" \
        --build-arg WORKER_NAME="$(whoami)@$(hostname)" \
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