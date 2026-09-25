#!/bin/sh
# Neutralize gcc's CRT tm_clones stubs in a linked binary.
#
# deregister_tm_clones and register_tm_clones are dead code in this program:
# the _ITM_* hooks are NULL, so both functions fall straight through to `ret`
# on every run. They do, however, decode into `mov edi, <bss>; jmp rax` and a
# stray `pop rax`, which look like usable register-loading gadgets and are not
# part of the intended chain. Overwrite both bodies with 0xC3 (ret).
#
# Field positions are found by scanning for the ".text" field, not by counting
# back from NF: readelf's flags column changes width per section, so NF-relative
# indexing silently picks up Size/EntSize instead of Address/Off.
#
# usage: sh strip-crt.sh
set -e

BIN=./chall
TADDR=$(readelf -SW "$BIN" | awk '{for(i=1;i<=NF;i++) if($i==".text"){print $(i+2); exit}}')
TOFF=$(readelf -SW "$BIN" | awk '{for(i=1;i<=NF;i++) if($i==".text"){print $(i+3); exit}}')
START=$(nm "$BIN" | awk '$3=="deregister_tm_clones"{print $1}')
END=$(nm "$BIN" | awk '$3=="__do_global_dtors_aux"{print $1}')

OFF=$((0x$START - 0x$TADDR + 0x$TOFF))
LEN=$((0x$END - 0x$START))

# dd conv=notrunc still happily extends a file, so a wrong offset would produce
# a multi-megabyte binary with the stubs left intact. Refuse instead.
SIZE=$(wc -c < "$BIN")
[ "$LEN" -gt 0 ] && [ "$OFF" -ge 0 ] && [ $((OFF + LEN)) -le "$SIZE" ] || {
    echo "strip-crt: refusing to write $LEN bytes at $OFF (file is $SIZE)" >&2
    exit 1
}

perl -e 'print "\xc3" x $ARGV[0]' "$LEN" |
dd of="$BIN" bs=1 seek="$OFF" conv=notrunc status=none
