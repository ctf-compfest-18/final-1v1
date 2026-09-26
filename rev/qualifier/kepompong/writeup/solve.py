#!/usr/bin/env python3
import re
import sys

from pwn import ELF

BLOB_KEY = bytes([0x9A, 0x47, 0xC3, 0x1E, 0x75, 0xB2, 0x6D, 0x08])
STAGE2_KEY = bytes([0x5B, 0xA7, 0x3E, 0xC9])

path = sys.argv[1] if len(sys.argv) > 1 else "../src/chall"
elf = ELF(path, checksec=False)

n = int.from_bytes(elf.read(elf.sym["stage2_enc_len"], 4), "little")
blob = elf.read(elf.sym["stage2_enc"], n)
stage2 = bytes(b ^ BLOB_KEY[i % len(BLOB_KEY)] for i, b in enumerate(blob))
print(f"[+] stage 2: {len(stage2)} bytes decrypted")

# each position compiles to:  xor dl, [rdi+off]   then   cmp dl, imm
wants = []
for m in re.finditer(rb"\x32\x57(.)\x80\xfa(.)", stage2, re.S):
    wants.append((m.group(1)[0], m.group(2)[0]))
first = re.search(rb"\x32\x17\xb9\x00\x00\x00\x00\x80\xfa(.)", stage2, re.S)
if first:
    wants.insert(0, (0, first.group(1)[0]))
wants.sort(key=lambda t: t[0])
print(f"[+] {len(wants)} per-byte comparisons recovered")

body = bytes(imm ^ STAGE2_KEY[off % len(STAGE2_KEY)] for off, imm in wants)
flag = "COMPFEST18{" + body.decode() + "}"
print(f"[+] {flag}")

check = [(i, b ^ STAGE2_KEY[i % len(STAGE2_KEY)]) for i, b in enumerate(body)]
assert check == wants, (check, wants)
print("[+] re-encrypt matches the stored comparison bytes")
