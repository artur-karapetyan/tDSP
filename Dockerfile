FROM ubuntu:18.04
RUN apt-get clean && apt-get update && apt-get install -y locales
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
WORKDIR /data
ADD ./requirements.txt /data
RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install python3.10 python3-dev python3-pip postgresql-client postgresql-server-dev-10
RUN apt-get update && apt-get install -y python3-pip
RUN apt-get update && apt-get install -y libjpeg-dev libpng-dev python-pil
RUN apt-get -y install curl zip unzip
RUN pip3 install --upgrade pip
RUN apt-get -y install cron
RUN pip3 install -r requirements.txt
# Preperation
COPY . /data