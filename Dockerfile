FROM python:3-alpine

ADD requirements/base.txt /ebooks/requirements/
ADD requirements/markov.txt /ebooks/requirements/

WORKDIR /ebooks/

RUN apk add --virtual .build-deps gcc musl-dev libffi-dev openssl-dev \
     && pip install -r requirements/base.txt \
     && pip install -r requirements/markov.txt \
     && apk del --purge .build-deps \
     && apk add bash \
     && ln -s data/config.json . \
     && ln -s data/posts.db .

ADD entrypoint.sh ./
RUN chmod +x entrypoint.sh

ADD *.py ./
ADD generators ./generators/
ADD third_party ./third_party/

ADD config.defaults.json ./

ADD schema.sql ./

RUN mkdir ./data

ENV POST_TIMINGS="*/30 * * * *"
ENV FETCH_TIMINGS="5 */2 * * *"

ENTRYPOINT [ "/ebooks/entrypoint.sh" ]
