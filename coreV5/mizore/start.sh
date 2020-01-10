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

    elif [ $1 == "notify" ] || [ $1 == "n" ] || [ $1 == "notifier" ]; then
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
            python3 worker.py notify
        fi

    elif [ $1 == "distribute" ] || [ $1 == "d" ] || [ $1 == "distributor" ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Detected a MacOS user, booting RQ manually"

            HOST="$(grep '^host = ' conf/izumi.toml | awk -F '"' '{print $2}')"
            PORT="$(grep '^port = ' conf/izumi.toml | awk -F '= ' '{print $2}' | awk 'NR==2')"
            PASSWORD="$(grep '^password = ' conf/izumi.toml | awk -F '"' '{print $2}')"

            rq worker \
                --url "redis://:$PASSWORD@$HOST:$PORT" \
                --name "$(whoami)@$(hostname):$(date +%Y%m%d.%H%M)" \
                distribute
        else
            echo "Booting RQ through worker script"
            python3 worker.py distribute
        fi

    elif [ $1 == "worker" ] || [ $1 == "work" ] || [ $1 == "w" ]; then

        ENCODE_SET="$(grep '^encode = ' conf/worker.toml | awk -F '= ' '{print $2}')"
        NOTIFY_SET="$(grep '^notify = ' conf/worker.toml | awk -F '= ' '{print $2}')"
        DISTRIBUTE_SET="$(grep '^distribute = ' conf/worker.toml | awk -F '= ' '{print $2}')"

        # Add a space at the end of names for correct queue appending
        [[ $ENCODE_SET == "false" ]] && ENCODE_MODE="" || ENCODE_MODE="encode "
        [[ $NOTIFY_SET == "false" ]] && NOTIFY_MODE="" || NOTIFY_MODE="notify "
        [[ $DISTRIBUTE_SET == "false" ]] && DISTRIBUTE_MODE="" || DISTRIBUTE_MODE="distribute "

        echo "Encode Mode: $ENCODE_SET"
        echo "Notify Mode: $NOTIFY_SET"
        echo "Distribute Mode: $DISTRIBUTE_SET"

        if [[ "$OSTYPE" == "darwin"* ]]; then
            echo "Detected a Mac OS user, booting RQ manually"

            HOST="$(grep '^host = ' conf/izumi.toml | awk -F '"' '{print $2}')"
            PORT="$(grep '^port = ' conf/izumi.toml | awk -F '= ' '{print $2}' | awk 'NR==2')"
            PASSWORD="$(grep '^password = ' conf/izumi.toml | awk -F '"' '{print $2}')"

            rq worker \
                --url "redis://:$PASSWORD@$HOST:$PORT" \
                --name "$(whoami)@$(hostname):$(date +%Y%m%d.%H%M)" \
                "$ENCODE_MODE""$NOTIFY_MODE""$DISTRIBUTE_MODE"

        else
            echo "Booting RQ through worker script"
            python3 worker.py "$ENCODE_MODE" "$NOTIFY_MODE" "$DISTRIBUTE_MODE"
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

        IMAGE_NAME="$(grep '^image_name = ' conf/encoder.toml | awk -F '"' '{print $2}')"
        CONTAINER_NAME="$(grep '^container_name = ' conf/encoder.toml | awk -F '"' '{print $2}')"

        echo "Docker image is '$IMAGE_NAME', container name is '$CONTAINER_NAME'"
        echo

        command docker run -d \
            --name "$CONTAINER_NAME" \
            -e DOCKER='true' \
            "$IMAGE_NAME"
        command docker logs -f "$CONTAINER_NAME"

    elif [ $1 == "notify" ] || [ $1 == "n" ] || [ $1 == "notifier" ]; then
        echo "Starting Izumi notifier worker in Docker"

        IMAGE_NAME="$(grep '^image_name = ' conf/notifier.toml | awk -F '"' '{print $2}')"
        CONTAINER_NAME="$(grep '^container_name = ' conf/notifier.toml | awk -F '"' '{print $2}')"

        echo "Docker image is '$IMAGE_NAME', container name is '$CONTAINER_NAME'"
        echo

        command docker run -d \
            --name "$CONTAINER_NAME" \
            -e DOCKER='true' \
            "$IMAGE_NAME"
        command docker logs -f "$CONTAINER_NAME"

    elif [ $1 == "work" ] || [ $1 == "w" ] || [ $1 == "worker" ]; then
        echo "Starting Izumi general worker in Docker"

        IMAGE_NAME="$(grep '^image_name = ' conf/worker.toml | awk -F '"' '{print $2}')"
        CONTAINER_NAME="$(grep '^container_name = ' conf/worker.toml | awk -F '"' '{print $2}')"

        echo "Docker image is '$IMAGE_NAME', container name is '$CONTAINER_NAME'"
        echo

        ENCODE_SET="$(grep '^encode = ' conf/worker.toml | awk -F '= ' '{print $2}')"
        NOTIFY_SET="$(grep '^notify = ' conf/worker.toml | awk -F '= ' '{print $2}')"
        DISTRIBUTE_SET="$(grep '^distribute = ' conf/worker.toml | awk -F '= ' '{print $2}')"

        [[ $ENCODE_SET == "false" ]] && ENCODE_MODE="" || ENCODE_MODE="encode"
        [[ $NOTIFY_SET == "false" ]] && NOTIFY_MODE="" || NOTIFY_MODE="notify"
        [[ $DISTRIBUTE_SET == "false" ]] && DISTRIBUTE_MODE="" || DISTRIBUTE_MODE="distribute"

        echo "Encode Mode: $ENCODE_SET"
        echo "Notify Mode: $NOTIFY_SET"
        echo "Distribute Mode: $DISTRIBUTE_SET"

        command docker run -d \
            --name "$CONTAINER_NAME" \
            -e DOCKER='true' \
            "$IMAGE_NAME" python3 /izumi/worker.py "$ENCODE_MODE" "$NOTIFY_MODE" "$DISTRIBUTE_MODE"
        command docker logs -f "$CONTAINER_NAME"

    fi
}

function helper {
    echo "Usage: ./start.sh {1} {2}"
    echo "{1}: docker || d || interactive || i"
    echo "{2}: izumi || i || encode || e || notify || n || distribute || d || worker || w"
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