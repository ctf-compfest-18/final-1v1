#!/bin/sh

exec socat \
TCP-LISTEN:1337,reuseaddr,fork \
EXEC:"setarch x86_64 -R /app/challenge"