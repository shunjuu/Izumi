# Get Python stuffs

FROM python:3

LABEL maintainer="Aleytia"

RUN apt-get update -y && \
	apt-get install apt-utils -y

COPY app/ /src/
COPY bin/ /bin2/

RUN pip3 install -r /src/requirements.txt

RUN chmod 700 /bin2/*

ENTRYPOINT ["sh", "-c", "python3 /src/encoder.py"]
