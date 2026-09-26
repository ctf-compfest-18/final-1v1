FROM pwn.red/jail
COPY --from=ubuntu@sha256:4f838adc7181d9039ac795a7d0aba05a9bd9ecd480d294483169c5def983b64d / /srv

COPY ./chall /srv/app/run
COPY ./flag.txt /srv/app/flag.txt
RUN chmod 0755 /srv/app/run

ENV JAIL_PORT=1337 JAIL_TIME=180
