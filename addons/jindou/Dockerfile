FROM golang:1.13.5-alpine

LABEL maintainer="Kyrielight"

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh

RUN go get "code.cloudfoundry.org/bytefmt"

COPY . /jindou/
RUN chmod 700 /jindou/*

ENTRYPOINT ["/jindou/start.sh", "i"]
