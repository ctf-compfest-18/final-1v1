# Kepompong — REV 4, self-decrypting stage

**Category:** Reverse Engineering · **Difficulty:** medium
**Flag:** `COMPFEST18{dump_th3_rwx_p4g3_th3n_x0r_1t_b4ck_0nc3!}`

---

## 1. Why static analysis comes up empty

Open `chall` in anything and look for the comparison. It is not there.

```
$ strings chall | grep -i compfest
COMPFEST18{
$ strings chall | grep dump_th3
$
```

`main` validates the wrapper, then does this:

```c
page = mmap(NULL, 4096, PROT_READ | PROT_WRITE | PROT_EXEC,
            MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
for (i = 0; i < stage2_enc_len; i++)
    ((unsigned char *)page)[i] = stage2_enc[i] ^ KEY[i % sizeof(KEY)];
stage2 = (unsigned long (*)(const unsigned char *))page;
puts(stage2(in + 11) ? "mekar" : "belum");
```

The real checker is a 676-byte XOR-encrypted blob in `.data`. It only becomes
instructions after the loop writes it to an anonymous RWX page, and it is called
through a function pointer, so there is no call target in the binary for a
disassembler to follow.

The blob is not compressed or packed, just XORed with a repeating 8-byte key
that sits in `.rodata` a few bytes away:

```
0x9A, 0x47, 0xC3, 0x1E, 0x75, 0xB2, 0x6D, 0x08
```

## 2. Path A — dynamic: break on the call, dump the page

The indirect call is the only `call rax` in `main`:

```
$ objdump -d -M intel chall | grep -B3 'call.*rax'
1332:  48 8d 7c 24 0b    lea    rdi,[rsp+0xb]
1337:  ff d0             call   rax
```

`main` starts at `0x1229`, so that is `main+0x10e`. Break there and `rax` is
already the page address:

```
$ printf 'COMPFEST18{AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA}\n' > in.txt
$ gdb -q -batch \
    -ex 'break *(main+0x10e)' \
    -ex 'run < in.txt' \
    -ex 'printf "page = %p\n", $rax' \
    -ex 'dump binary memory page.bin $rax ($rax+400)' \
    ./chall
Breakpoint 1, 0x0000555555555337 in main ()
page = 0x7ffff7fbb000

$ objdump -D -b binary -m i386:x86-64 -M intel page.bin | head -14
   0:  f3 0f 1e fa          endbr64
   4:  c6 44 24 ff 5b       mov    BYTE PTR [rsp-0x1],0x5b
   9:  c6 44 24 fe a7       mov    BYTE PTR [rsp-0x2],0xa7
   e:  c6 44 24 fd 3e       mov    BYTE PTR [rsp-0x3],0x3e
  13:  c6 44 24 fc c9       mov    BYTE PTR [rsp-0x4],0xc9
  18:  0f b6 54 24 ff       movzx  edx,BYTE PTR [rsp-0x1]
  1d:  32 17                xor    dl,BYTE PTR [rdi]
  24:  80 fa 3f             cmp    dl,0x3f
  27:  0f 85 73 02 00 00    jne    0x2a0
  2d:  0f b6 54 24 fe       movzx  edx,BYTE PTR [rsp-0x2]
  32:  32 57 01             xor    dl,BYTE PTR [rdi+0x1]
  35:  80 fa d2             cmp    dl,0xd2
```

The input there is 40 `A`s. It does not matter what you type as long as the
length check passes, because the page is decrypted before stage 2 ever runs.

## 3. Path B — static: decrypt the blob yourself

No debugger needed. The binary is not stripped, so the blob is addressable by
symbol:

```
$ nm chall | grep stage2
0000000000004040 D stage2_enc
0000000000004020 D stage2_enc_len
```

Read it, XOR with the key, disassemble the result as raw bytes:

```python
blob = elf.read(elf.sym['stage2_enc'], 676)
stage2 = bytes(b ^ KEY[i % 8] for i, b in enumerate(blob))
```

```
$ objdump -D -b binary -m i386:x86-64 -M intel stage2.bin
```

Same five immediates, byte for byte. Both paths converge here, which is the
point: neither is a shortcut past the other.

## 4. Why the dump is not the flag

This is the part that matters. If stage 2 ended in a `memcmp` against a literal
flag, dumping the page would *be* the solve. The string would sit in the dump in
plaintext and the challenge would be over in the time it takes to run `strings`
on `page.bin`.

It does not. Stage 2 never stores the flag. It stores a 4-byte repeating key and
40 comparison bytes, and checks one input byte at a time:

```c
unsigned long check(const unsigned char *in)
{
    volatile unsigned char k0 = 0x5B;
    volatile unsigned char k1 = 0xA7;
    volatile unsigned char k2 = 0x3E;
    volatile unsigned char k3 = 0xC9;

    if ((in[ 0] ^ k0) != 0x3F) return 0;
    if ((in[ 1] ^ k1) != 0xD2) return 0;
    if ((in[ 2] ^ k2) != 0x53) return 0;
    ...
    if ((in[39] ^ k3) != 0xE8) return 0;

    return 1;
}
```

No packing, no 64-bit groups, no advancing state. Position `i` uses key byte
`i % 4`, so the whole key is the four immediates stored to the stack in the
prologue. Every comparison byte is an inline literal.

The `volatile` is load-bearing and not decoration. Drop it and gcc `-O1`
constant-folds `(in[i] ^ K) != M` into `cmp BYTE PTR [rdi+i], M^K`, which puts
the plaintext flag straight into the dump as immediates:

```
   9:  80 3f 64             cmp    BYTE PTR [rdi],0x64        <- 'd'
  12:  80 7f 01 75          cmp    BYTE PTR [rdi+0x1],0x75    <- 'u'
  1c:  80 7f 02 6d          cmp    BYTE PTR [rdi+0x2],0x6d    <- 'm'
```

At that point `strings page.bin` is the entire challenge. With `volatile` the
key stays a real memory operand, the `xor` survives into the emitted code, and
the dump carries key-xor-flag rather than flag.

So recovering the flag from the dump takes exactly one pass:

```python
K = bytes([0x5B, 0xA7, 0x3E, 0xC9])
body = bytes(cmp[i] ^ K[i % 4] for i in range(40))
```

One XOR per byte against a 4-byte key you can read off the first five
instructions. That is the decode round, and it is the whole point: dumping the
page gets you the check, not the answer.

Body is 40 bytes, one comparison per byte, no padding.

## 5. Solve

```
$ python3 solve.py chall
[+] stage 2: 676 bytes decrypted
[+] compare immediates: ['0xc5132244c6d6633f', '0x11cfa6c44e4ce484', '0x8e243828decf4968', '0x429989ef0764e4eb', '0xd748357586e47d38']
[+] COMPFEST18{dump_th3_rwx_p4g3_th3n_x0r_1t_b4ck_0nc3!}
[+] re-encrypt matches the immediates

$ echo 'COMPFEST18{dump_th3_rwx_p4g3_th3n_x0r_1t_b4ck_0nc3!}' | ./chall
kunci: mekar
```

`solve.py` takes the static path end to end: symbol lookup, XOR, regex the
comparison bytes out of the `xor dl, [rdi+off]` / `cmp dl, imm` pairs, then XOR
each one against its key byte. It then re-encrypts its own answer and asserts it reproduces the immediates,
so a wrong seed or a wrong recurrence fails loudly instead of printing garbage
that happens to be 40 characters long.

## 6. The build constraint that actually bites

Stage 2 is copied as raw bytes to an address nobody chose in advance. Anything
in it that needs fixing up at load time has nothing to fix it up, so `stage2.o`
has to carry **zero relocations**. `build.sh` asserts this and refuses to
continue:

```
[2/5] assert stage2.o is relocation-free

There are no relocations in this file.
```

That is why stage 2 has no globals, no string literals, no lookup tables and no
calls leaving the file, and why the five compare values are immediates rather
than an array. It is also why the 40 checks are written out longhand: as a loop
over a constant array of key and comparison bytes, that array would land in
`.rodata` and take a RIP-relative reference with it.

One flag beyond the specified set was needed: `-fno-asynchronous-unwind-tables`.
Without it gcc emits `.eh_frame`, which carries one `R_X86_64_PC32` against
`.text`. That relocation is harmless in practice, since
`objcopy --only-section=.text` throws `.eh_frame` away, but it makes
`readelf -r` non-empty and the step-2 assertion unsatisfiable.

## 7. Layout

```
./
  challenge.yml         CTFd challenge metadata
  README.md             author-facing
src/
  chall.c  stage2.c  build.sh  Dockerfile.build    source and build
  chall                                           build output
  README.player.md                                player README, packed into the zip
public/
  dist-kepompong.zip    the only thing players get: chall + README.md, no source
writeup/
  solve.py  README.md  readelf-stage2.txt
```
