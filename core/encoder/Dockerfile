# Get Python stuffs
FROM python:3.6.8-alpine3.8

LABEL maintainer="Aleytia"

RUN apk update && apk upgrade

COPY app/requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt

COPY bin/ /bin2/
RUN chmod 700 /bin2/*

COPY app/ /src/

ENTRYPOINT ["sh", "-c", "python3 /src/encoder.py"]