#!/usr/bin/env python3
"""Kepompong - static solve. Never runs the binary, never attaches a debugger.

  1. pull the encrypted stage-2 blob straight out of chall
  2. XOR it with the 8-byte key stage 1 uses
  3. read the five 64-bit compare immediates out of the decrypted code
  4. undo the rolling XOR to get the flag back

  usage: python3 solve.py [path/to/chall]
"""
import re
import sys

from pwn import ELF

# stage 1: static const unsigned char KEY[8]
KEY = bytes([0x9A, 0x47, 0xC3, 0x1E, 0x75, 0xB2, 0x6D, 0x08])

# stage 2: unsigned char k = 0x5B;  k = k * 31 + 17;
SEED, MUL, ADD = 0x5B, 31, 17

path = sys.argv[1] if len(sys.argv) > 1 else "chall"
elf = ELF(path, checksec=False)

blob = elf.read(elf.sym["stage2_enc"],
                int.from_bytes(elf.read(elf.sym["stage2_enc_len"], 4), "little"))
stage2 = bytes(b ^ KEY[i % len(KEY)] for i, b in enumerate(blob))
print(f"[+] stage 2: {len(stage2)} bytes decrypted")

# `movabs rcx, imm64` / `movabs rax, imm64` -> 48 b9 / 48 b8 + 8 little-endian bytes
wants = [int.from_bytes(m.group(1), "little")
         for m in re.finditer(rb"\x48[\xb8\xb9](.{8})", stage2, re.S)]
print(f"[+] compare immediates: {[hex(w) for w in wants]}")

k = SEED
body = bytearray()
for w in wants:
    for i in range(8):
        body.append(((w >> (8 * i)) & 0xFF) ^ k)
        k = (k * MUL + ADD) & 0xFF

flag = "COMPFEST18{" + body.decode() + "}"
print(f"[+] {flag}")

# re-encrypt and confirm we land back on the immediates we read
k = SEED
check = []
for c in range(len(body) // 8):
    v = 0
    for i in range(8):
        v |= (body[c * 8 + i] ^ k) << (8 * i)
        k = (k * MUL + ADD) & 0xFF
    check.append(v)
assert check == wants, (check, wants)
print("[+] re-encrypt matches the immediates")
