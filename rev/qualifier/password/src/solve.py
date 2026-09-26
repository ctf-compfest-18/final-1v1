#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pwn import *
from pwncli import IO_FILE_plus_struct
from keystone import *
from capstone import *

bin_path = "./chall"
if args.EXE or bin_path:
    exe = context.binary = ELF(args.EXE or bin_path)
else:
    exe = None
context.terminal = "wt.exe wsl".split()
context.log_level = "debug" if args.DEBUG else "info"


libc_path = None
ld_path = None
libc = ELF(libc_path) if libc_path else (exe.libc if exe else None)
ld = ELF(ld_path) if ld_path else None


class LogAddressHex:
    def __getattribute__(self, name):
        try:
            resolved = eval(name)
        except:
            error(f'"{name}" doesn\'t exist')
            return lambda: ...

        if hasattr(resolved, "address"):
            resolved = getattr(resolved, "address")

            if not resolved & 0xFFF:
                success(term.text.bold_green(f"{name}.address & 0xFFF == 0"))
            else:
                warn(term.text.bold_yellow(f"{name}.address & 0xFFF != 0"))

        info(term.text.blue(f"{name} : {resolved:#x}"))
        return lambda: ...


logx = LogAddressHex()


def start_local(argv=[], *a, **kw):
    """Execute the target binary locally"""
    kw["env"] = {"SHELL": "/bin/sh"}
    if args.GDB:
        return gdb.debug([exe.path] + argv, gdbscript=gdbscript, *a, **kw)
    else:
        return process([exe.path] + argv, *a, **kw)


def start_remote(argv=[], *a, **kw):
    """Connect to the process on the remote host"""
    io = connect(host, port)
    if args.GDB:
        gdb.attach(io, gdbscript=gdbscript)
    return io


def start(argv=[], *a, **kw):
    """Start the exploit against the target."""
    if args.LOCAL or args.LOCAL_LIBC:
        return start_local(argv, *a, **kw)
    else:
        return start_remote(argv, *a, **kw)


def fasm(code, pp=True):
    ks = Ks(KS_ARCH_X86, KS_MODE_64 if context.arch == "amd64" else KS_MODE_32)
    if pp:
        code = cpp(code)
    encoding, _ = ks.asm(code)
    return bytes(encoding)


def fdisasm(code, vma=0x0):
    md = Cs(CS_ARCH_X86, CS_MODE_64 if context.arch == "amd64" else CS_MODE_32)
    instructions = []
    for i in md.disasm(code, vma):
        instructions.append("0x{:x}:\t{}\t{}".format(i.address, i.mnemonic, i.op_str))
    return "\n".join(instructions)


def ua(x):
    return int.from_bytes(x, "little")


def se(x):
    return str(x).encode()


def cyc(x):
    n = 8 if context.arch == "amd64" else 4
    return cyclic(x, n=n)


def solve_pow(crib=b"pwn.red"):
    if args.LOCAL:
        return
    with log.progress("Solving PoW..."):
        cmd = p.recvline_contains(crib).decode().strip()
        output = subprocess.check_output(cmd, shell=True)
        p.sendline(output)


def hoa(libc=libc, func=None, arg="sh", IO_target=None):
    func = libc.sym.system if func is None else func
    IO_target = libc.sym["_IO_2_1_stderr_"] if IO_target is None else IO_target
    return IO_FILE_plus_struct().house_of_apple2_execmd_when_exit(
        IO_target,
        libc.sym["_IO_wfile_jumps"],
        func,
        arg,
    )


def s(*k, **a):
    p.send(*k, **a)


def sl(*k, **a):
    p.sendline(*k, **a)


def sa(*k, **a):
    p.sendafter(*k, **a)


def sla(*k, **a):
    p.sendlineafter(*k, **a)


def r(*k, **a):
    p.recv(*k, **a)


def ru(*k, **a):
    p.recvuntil(*k, **a)


def rl(*k, **a):
    p.recvline(*k, **a)


def rlc(*k, **a):
    p.recvline_contains(*k, **a)


def rlse(x=None):
    if x is None:
        return eval(p.recvline().split()[-1])
    return p.recvline_contains(x).split()[-1]


_, host, port = "nc host port".split()

gdbscript = """
b *(main+0)
continue
""".format(**locals())

p = start()

from ctypes import CDLL

glibc = CDLL("/usr/lib/x86_64-linux-gnu/libc.so.6")

seed = glibc.time(0) >> 1
key = [
    19073089,
    6519095881,
    135435401,
    9536069,
    2241026101,
    180084399,
    9472328635,
    881011114,
]

glibc.srand(seed)
"""
  v1 = (__int64 *)&qword_4080;
  v2 = s1;
  do
  {
    v3 = *v1;
    for ( i = 0; i != 67; ++i )
    {
      v5 = v3 ^ v0;
      if ( 030473047305 * i < 0x13B13B14 )
        v5 ^= 0x43uLL;
      v3 += 324;
      v0 = rand() & 0x1234567 ^ (unsigned __int64)v5;
    }
    v6 = v2;
    v2 += 4;
    ++v1;
    result = snprintf(v6, 5u, "%04lx", (unsigned __int16)v0);
  }
  while ( v2 != &s1[32] );

"""
passw = ""
v0 = 0
for k in key:
    for i in range(67):
        v5 = k ^ v0
        if ((0o030473047305 * i) & 0xFFFFFFFF) < 0x13B13B14:
            v5 ^= 0x43
        k += 324
        k &= 0xFFFFFFFFFFFFFFFF
        v0 = glibc.rand() & 0x1234567 ^ (v5 & 0xFFFFFFFFFFFFFFFF)
    v0 &= 0xFFFF
    passw += f"{v0:#4x}"[2:]
print(passw)
sl(passw)

p.interactive()
