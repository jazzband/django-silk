FROM python:3.8-alpine

# Some system dependencies
RUN apk update -qq && apk add build-base jpeg-dev zlib-dev

ENV APP_HOME=/usr/src/silk
RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME

COPY . /app/

RUN pip install tox

CMD ["tox"]
