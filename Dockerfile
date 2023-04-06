FROM python:3.10-alpine

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN mkdir /app
COPY ./requirements.txt /app

# Install required package
RUN apk update && \
    apk add --no-cache --virtual .build-deps \
    ca-certificates gcc postgresql-dev linux-headers musl-dev \
    libffi-dev jpeg-dev zlib-dev \
    git bash

# Install requirements.txt
RUN pip install -r /app/requirements.txt

COPY ./src/tdsp/ /app
WORKDIR /app

CMD [ "python", "manage.py", "runserver", "0.0.0.0:9090" ]