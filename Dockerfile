FROM python:3.10.4-slim-buster
RUN apt update && apt install -y docker.io

COPY . /src
WORKDIR /src

ENV PYTHONPATH "${PYTHONPATH}:/src/docker_rest_app"
RUN ["pip", "install", "-r", "requirements.txt"]
