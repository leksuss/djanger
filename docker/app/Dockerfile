FROM python:3.9-slim

RUN apt update && apt install -y libpcre3 mime-support postgresql-client

WORKDIR /home/src

COPY ../../requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt