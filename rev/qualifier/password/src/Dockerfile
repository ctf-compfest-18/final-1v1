FROM alpine@sha256:4bcff63911fcb4448bd4fdacec207030997caf25e9bea4045fa6c8c44de311d1

RUN adduser -D -u 1000 ctf

WORKDIR /app
COPY --chmod=0555 chall /app/chall
COPY --chmod=0555 ld-linux-x86-64.so.2 /lib64/ld-linux-x86-64.so.2
COPY --chmod=0555 libc.so.6 /lib/x86_64-linux-gnu/libc.so.6
COPY --chown=ctf:ctf --chmod=0400 flag.txt /app/flag.txt

USER ctf
EXPOSE 1337

CMD ["nc", "-lk", "-p", "1337", "-e", "/app/chall"]
