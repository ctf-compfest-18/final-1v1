FROM ubuntu:24.04

RUN apt-get update && \
    apt-get install -y \
        socat \
        util-linux && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY challenge /app/challenge
COPY start.sh /app/start.sh

RUN chmod +x /app/challenge /app/start.sh

RUN echo "COMPFEST18{we_have_rop_mprotect_at_home_ahhh_chall}" > /flag.txt
RUN chmod 444 /flag.txt

EXPOSE 1337

CMD ["/app/start.sh"]