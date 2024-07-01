# pull official base image
FROM python:3.12-alpine

# set work directory
RUN mkdir /molniya/
WORKDIR /molniya
# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update

RUN pip install --upgrade pip
COPY /requirements/requirements.dev.txt .
RUN pip install -r requirements.dev.txt
ENV PYTHONPATH="/molniya/src"

COPY /src ./src
COPY /env ./env
CMD celery --app=pkg.celery_tools.tools:celery_app flower
