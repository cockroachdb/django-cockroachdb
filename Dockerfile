FROM ubuntu:18.04

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get -y install python3 python3-dev python3-pip build-essential postgresql postgresql-contrib libpq-dev wget git
