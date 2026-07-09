FROM ubuntu@sha256:786a8b558f7be160c6c8c4a54f9a57274f3b4fb1491cf65146521ae77ff1dc54

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y --no-install-recommends socat

RUN rm -rf /var/lib/apt/lists/*
RUN     useradd ctf
WORKDIR /home/ctf

COPY ./chall /home/ctf/
COPY ./flag.txt /home/ctf/

RUN chown -R root:root  /home/ctf
RUN chmod -R 755        /home/ctf

EXPOSE 1337
ENTRYPOINT ["socat", "TCP-LISTEN:1337,reuseaddr,fork,nodelay,su=ctf", "EXEC:'timeout 60 ./chall'"]
