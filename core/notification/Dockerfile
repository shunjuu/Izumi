# Get Python stuffs

FROM python:3.6.8-alpine3.8

LABEL maintainer="Aleytia"

RUN apk update && apk upgrade

COPY app/requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt

COPY app/ /src/

ENTRYPOINT ["sh", "-c", "python3 /src/notification.py"]