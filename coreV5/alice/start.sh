#!/bin/bash

docker run -d \
    --cap-add=NET_ADMIN \
    --name=alice \
    -p 9080:9080 \
    -p 9443:9443 \
    -p 8118:8118 \
    -v "$(pwd)/data:/data" \
    -v "$(pwd)/config:/config" \
    -e VPN_ENABLED=yes \
    -e VPN_PROV=custom \
    -e STRICT_PORT_FORWARD=no \
    -e ENABLE_PRIVOXY=no \
    -e ENABLE_AUTODL_IRSSI=no \
    -e ENABLE_RPC2=no \
    -e ENABLE_RPC2_AUTH=no \
    -e ENABLE_WEBUI_AUTH=no \
    -e LAN_NETWORK=192.168.1.0/24 \
    -e NAME_SERVERS=8.8.8.8,8.8.4.4,1.1.1.1 \
    -e PUID=0 \
    -e PGID=0 \
    -e PHP_TZ=UTC \
    -e DEBUG=false \
    binhex/arch-rtorrentvpn

# Includes definitions for Traefik
# Add your OpenVPN configurations!