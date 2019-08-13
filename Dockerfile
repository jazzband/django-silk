FROM python:3.7-alpine
MAINTAINER Viralize

# Some system dependencies
RUN apk update -qq && apk add build-base jpeg-dev zlib-dev

ENV APP_HOME=/usr/src/silk
RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME

COPY project/test-requirements.txt ./
RUN pip3 install -r test-requirements.txt

COPY setup.py setup.cfg README.md ./
COPY silk silk
COPY project project
RUN pip3 install -e .

CMD ["project/run_tests.sh"]
