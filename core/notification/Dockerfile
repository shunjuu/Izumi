# Get Python stuffs

FROM python:3

LABEL maintainer="Aleytia"

RUN apt-get update -y && \
    apt-get install apt-utils -y

RUN pip3 install flask requests pyyaml hurry.filesize anitopy colorthief

COPY app/ /src/

ENTRYPOINT ["sh", "-c", "python3 /src/notification.py"]