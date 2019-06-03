#Get Python stuffs

FROM python:3.7-alpine

LABEL maintainer="Aleytia"

RUN apk update && \
	apk add inotify-tools

COPY app/ /src/
COPY bin/ /rclone/

RUN pip3 install -r /src/requirements.txt

RUN chmod 700 /rclone/*
RUN chmod 700 /src/bin/yq

ENTRYPOINT ["sh", "-c", "/src/watch.sh"]
