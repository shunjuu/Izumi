#!/bin/bash

function interactive {
    # Start Izumi in interactive mode
    echo "Starting Izumi applet server in interactive mode."
    if [ $1 == "izumi" ] || [ $1 == "i" ]; then
        python3 izumi.py

    elif [ $1 == "encode" ] || [ $1 == "e" ] || [ $1 == "encoder" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Detected a MacOS user, booting RQ manually"

            HOST="$(grep '^host = ' conf/izumi.toml | awk -F '"' '{print $2}')"
            PORT="$(grep '^port = ' conf/izumi.toml | awk -F '= ' '{print $2}' | awk 'NR==2')"
            PASSWORD="$(grep '^password = ' conf/izumi.toml | awk -F '"' '{print $2}')"

            rq worker \
                --url "redis://:$PASSWORD@$HOST:$PORT" \
                --name "$(whoami)@$(hostname):$(date +%Y%m%d.%H%M)" \
                encode
        else
            echo "Booting RQ through worker script"
            python3 worker.py encode
        fi

    fi
}

function docker {

    # Start Izumi in Docker mode
    if [ $1 == "izumi" ] || [ $1 == "i" ]; then
        echo "Starting Izumi applet server in Docker"

        FLASK_PORT="$(grep '^port = ' conf/izumi.toml | awk -F '= ' '{print $2}' | awk 'NR==1')"
        DOCKER_PORT="$(grep '^docker_port = ' conf/izumi.toml | awk -F '= ' '{print $2}')"
        IMAGE_NAME="$(grep '^image_name = ' conf/izumi.toml | awk -F '"' '{print $2}')"
        CONTAINER_NAME="$(grep '^container_name = ' conf/izumi.toml | awk -F '"' '{print $2}')"

        echo "Docker image is '$IMAGE_NAME', container name is '$CONTAINER_NAME'"
        echo

        command docker run -d \
            -p "127.0.0.1:$DOCKER_PORT:$FLASK_PORT" \
            --name "$CONTAINER_NAME" \
            -e DOCKER='true' \
            "$IMAGE_NAME"
        command docker logs -f "$CONTAINER_NAME"

    elif [ $1 == "encode" ] || [ $1 == "e" ] || [ $1 == "encoder" ]; then
        echo "Starting Izumi encoding worker in Docker"
        command docker run -d \
            --name "izumi-v5-encoder" \
            -e DOCKER='true' \
            "izumi/v5/encoder"
        command docker logs -f "izumi-v5-encoder"

    fi
}

function helper {
    echo "Usage: ./start.sh {1} {2}"
    echo "{1}: docker || d || interactive || i"
    echo "{2}: izumi || i || encode || e"
}

case "$1" in

    "docker"|"d")
        docker $2
        ;;

    "interactive"|"i")
        interactive $2
        ;;

    *)
        helper
        ;;

esac