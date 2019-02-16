#Get Python stuffs

FROM python:3

LABEL maintainer="Aleytia"

RUN apt-get update -y && \
	apt-get install apt-utils -y && \
	apt-get install inotify-tools -y

RUN pip3 install requests hurry.filesize anitopy pyyaml

COPY app/ /src/
COPY bin/ /rclone/

ENTRYPOINT ["sh", "-c", "/src/watch.sh"]