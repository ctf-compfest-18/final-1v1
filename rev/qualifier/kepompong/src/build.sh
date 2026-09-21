#!/bin/sh
# Reproducible 5-step build. Run from /src.
set -eu

KEY_PERL='0x9A,0x47,0xC3,0x1E,0x75,0xB2,0x6D,0x08'

echo "[1/5] compile stage 2 (PIC, freestanding)"
gcc -c -fPIC -O1 -fno-stack-protector -nostdlib -fno-asynchronous-unwind-tables -o stage2.o stage2.c

echo "[2/5] assert stage2.o is relocation-free"
readelf -r stage2.o > readelf-stage2.txt
if grep -qE '^[0-9a-f]{8,}' readelf-stage2.txt; then
    echo "FAIL: stage2.o carries relocations -- stage 2 would crash at runtime." >&2
    cat readelf-stage2.txt >&2
    exit 1
fi
cat readelf-stage2.txt

echo "[3/5] extract raw .text"
objcopy -O binary --only-section=.text stage2.o stage2.bin

echo "[4/5] XOR-encrypt and emit C array"
perl -e '
    my @k = ('"$KEY_PERL"');
    binmode STDIN; binmode STDOUT;
    my $i = 0;
    while (read(STDIN, my $b, 1)) { print chr(ord($b) ^ $k[$i++ % 8]); }
' < stage2.bin > stage2.enc
xxd -i stage2.enc > stage2_blob.h

echo "[5/5] compile stage 1"
gcc -O1 -fno-stack-protector -o chall chall.c

echo "OK: chall $(wc -c < chall) bytes, stage2 blob $(wc -c < stage2.bin) bytes"
