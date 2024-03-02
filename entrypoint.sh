#!/bin/bash

set -xe

(echo "${POST_TIMINGS} cd /ebooks/ && python gen.py"; \
 echo "${FETCH_TIMINGS} cd /ebooks/ && python fetch_posts.py"; \
 echo "@reboot cd /ebooks/ && python reply.py") | crontab -

test -f data/posts.db || (python fetch_posts.py && exit)

exec crond -f -L /dev/stdout
