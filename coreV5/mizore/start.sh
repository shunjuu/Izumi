#!/bin/bash

function interactive {
    # Start Izumi in interactive mode
    echo "Starting Izumi applet server in interactive mode"
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
                --name "$(whoami)@$(hostname)" \
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
        command docker run -d \
            -p "17000:8080" \
            --name "izumi-v5-applet" \
            -e DOCKER='true' \
            "izumi/v5/applet"
        command docker logs -f "izumi-v5-applet"

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