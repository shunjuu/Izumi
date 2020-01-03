#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

BOT_TOKEN="$(grep '^token = ' $DIR/config.toml | awk -F '"' '{print $2}')"
CHAT_ID="$(grep '^chat_id = ' $DIR/config.toml | awk -F '"' '{print $2}')"


function docker {
    command docker run -d \
        --name "izumi-v5-jindou" \
        -p "22150:22150" \
        izumi/v5/jindou

    command docker logs -f izumi-v5-jindou
}

function interactive {
    go run "$DIR/jindou.go" "$BOT_TOKEN" "$CHAT_ID"
}

case "$1" in

    "docker"|"d")
        docker
        ;;

    "interactive"|"i")
        interactive
        ;;

esac