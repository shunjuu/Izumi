FROM python:3.8-slim

# I am the author!
LABEL maintainer="Kyrielight"

# Set timezone
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Indicate Docker mode to the container
ENV DOCKER=true

# Update our image
RUN apt-get update -y && \
    apt-get install apt-utils gcc python3-dev -y

# Install dependencies
COPY requirements.txt /opt/requirements.txt
RUN pip3 install -r /opt/requirements.txt && rm /opt/requirements.txt

# Copy project files
COPY . /izumi/
RUN chmod 700 /izumi/bin/*

# Set the worker name through use of environment properties
ARG WORKER_NAME
ENV WORKER_NAME=${WORKER_NAME}

# Explicitly call Python3 - this registers python3 as the root so SIGTERM can get passed
ENTRYPOINT ["python3", "/izumi/worker.py", "distribute"]