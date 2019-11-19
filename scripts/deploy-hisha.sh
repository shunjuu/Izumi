#!/bin/bash

HISHA="../modules/hisha/hisha.py"

# Two core use Hisha: Distributor and Notification
DISTRIBUTOR_HISHA="../core/distributor/app/bin/hisha.py"
NOTIFICATION_HISHA="../core/notification/app/bin/hisha.py"

deploy_distributor() {
	echo "Deploy Hisha to Distributor"
	cp "$HISHA" "$DISTRIBUTOR_HISHA"
}

deploy_notification() {
	echo "Deploying Hisha to Notification"
	cp "$HISHA" "$NOTIFICATION_HISHA"
}

# Main logic
if [ -z "$1" ]; then

	echo "Deploying Hisha to all modules"
	deploy_distributor
	deploy_notification

elif [ "$1" = "distributor" ]; then

	deploy_distributor

elif [ "$1" = "notification" ]; then

	deploy_notification

fi