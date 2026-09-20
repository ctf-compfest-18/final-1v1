#!/usr/bin/env python3

import re
import subprocess
import sys
import time
from pathlib import Path


binary = Path(sys.argv[1] if len(sys.argv) > 1 else "./chall").resolve()
loader = binary.with_name("ld-linux-x86-64.so.2")
argv = [binary]
if loader.exists() and binary.with_name("libc.so.6").exists():
    argv = [loader, "--library-path", str(binary.parent), binary]

process = subprocess.Popen(
    argv,
    cwd=binary.parent,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
)

password = None
for _ in range(100):
    with open(f"/proc/{process.pid}/maps") as maps:
        regions = []
        for line in maps:
            fields = line.split()
            if len(fields) >= 6 and fields[1] == "rw-p" and fields[-1] == str(binary):
                start, end = fields[0].split("-")
                regions.append((int(start, 16), int(end, 16)))

    with open(f"/proc/{process.pid}/mem", "rb", buffering=0) as memory:
        for start, end in regions:
            memory.seek(start)
            data = memory.read(end - start)
            match = re.search(rb"(?<![0-9a-f])[0-9a-f]{32}\x00", data)
            if match:
                password = match.group()[:-1]
                break

    if password:
        break
    time.sleep(0.01)

if password is None:
    process.kill()
    raise SystemExit("password not found in process memory")

print(f"[+] pid: {process.pid}", flush=True)
print(f"[+] password: {password.decode()}", flush=True)
output, _ = process.communicate(password + b"\n")
sys.stdout.buffer.write(output)
