# Get Python stuffs

FROM python:3

LABEL maintainer="Aleytia"

RUN apt-get update -y && \
    apt-get install apt-utils -y

COPY app/ /src/

RUN pip3 install -r /src/requirements.txt

ENTRYPOINT ["sh", "-c", "python3 /src/notification.py"]