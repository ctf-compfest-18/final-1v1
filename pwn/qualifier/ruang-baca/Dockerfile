# ---- build stage: the pinned base the challenge is compiled on -------------
FROM ubuntu@sha256:b8b6ee6aa931ecd9d0d952abc34dc0e5f7c6a30c6bb71b079fe399fde0329c02 AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc libc6-dev make libseccomp-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY src/chall.c src/Makefile ./
RUN make

# ---- rootfs the jail chroots into -----------------------------------------
# The jail chroots to /srv, so /flag.txt here is /flag.txt to the challenge -
# which is the literal path the banner advertises.
FROM ubuntu@sha256:b8b6ee6aa931ecd9d0d952abc34dc0e5f7c6a30c6bb71b079fe399fde0329c02 AS chroot
COPY --from=build /src/chall /app/run
COPY src/flag.txt /flag.txt
RUN chmod 555 /app/run && chmod 444 /flag.txt

# ---- serve -----------------------------------------------------------------
# pwn.red/jail (redpwn jail): nsjail forks a fresh, isolated process per TCP
# connection. docker-compose.yml overrides the JAIL_* limits below.
FROM pwn.red/jail:0.3.1
COPY --from=chroot / /srv
ENV JAIL_PORT=5600 JAIL_TIME=600 JAIL_MEM=256M JAIL_PIDS=32 JAIL_CPU=100
EXPOSE 5600
