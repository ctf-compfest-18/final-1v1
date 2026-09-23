FROM ubuntu@sha256:4f838adc7181d9039ac795a7d0aba05a9bd9ecd480d294483169c5def983b64d

RUN apt-get update && \
    apt-get install -y --no-install-recommends socat && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 ctf

WORKDIR /app
COPY --chmod=0555 chall /app/chall
COPY --chown=ctf:ctf --chmod=0400 flag.txt /app/flag.txt

USER ctf
EXPOSE 1337

CMD ["socat", "-T60", "TCP-LISTEN:1337,reuseaddr,fork,max-children=32", "EXEC:/app/chall,stderr"]
