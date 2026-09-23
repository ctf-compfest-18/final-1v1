FROM pwn.red/jail

# Copy an Ubuntu userspace into the jailed rootfs
COPY --from=ubuntu@sha256:786a8b558f7be160c6c8c4a54f9a57274f3b4fb1491cf65146521ae77ff1dc54 / /srv

# Challenge files
COPY ./src/chall /srv/app/chall
COPY ./src/flag.txt /srv/app/flag.txt

# Make the binary executable and tell the jail what to run
RUN chmod 755 /srv/app/chall && \
    ln -s /app/chall /srv/app/run

# Jail configuration
ENV JAIL_TIME=60
ENV JAIL_MEM=64M
ENV JAIL_PIDS=16
ENV JAIL_CPU=100

EXPOSE 5000