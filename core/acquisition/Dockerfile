#Get Python stuffs

FROM python:3

LABEL maintainer="Aleytia"

RUN apt-get update -y && \
	apt-get install apt-utils -y && \
	apt-get install inotify-tools -y

COPY app/ /src/
COPY bin/ /rclone/

RUN pip3 install -r /src/requirements.txt

RUN chmod 700 /rclone/*
RUN chmod 700 /src/bin/yq

ENTRYPOINT ["sh", "-c", "/src/watch.sh"]