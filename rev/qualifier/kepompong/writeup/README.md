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

The real checker is a 388-byte XOR-encrypted blob in `.data`. It only becomes
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

$ objdump -D -b binary -m i386:x86-64 -M intel page.bin | grep movabs
  42:  48 b9 3f 63 d6 c6 44   movabs rcx,0xc5132244c6d6633f
  8f:  48 b9 84 e4 4c 4e c4   movabs rcx,0x11cfa6c44e4ce484
  dc:  48 b9 68 49 cf de 28   movabs rcx,0x8e243828decf4968
 129:  48 b9 eb e4 64 07 ef   movabs rcx,0x429989ef0764e4eb
 16d:  48 b8 38 7d e4 86 75   movabs rax,0xd748357586e47d38
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
blob = elf.read(elf.sym['stage2_enc'], 388)
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

It does not. Stage 2 never stores the flag. It transforms your input and
compares the transform:

```c
#define GROUP(base, want)                                              \
    do {                                                               \
        unsigned long v = 0;                                           \
        int i;                                                         \
        for (i = 0; i < 8; i++) {                                      \
            v |= (unsigned long)(unsigned char)(in[(base) + i] ^ k)    \
                 << (8 * i);                                           \
            k = (unsigned char)(k * 31 + 17);                          \
        }                                                              \
        if (v != (want)) return 0;                                     \
    } while (0)
```

Each byte is XORed against a **rolling** key, the eight results are packed
little-endian into a 64-bit word, and that word is compared to an immediate. The
key starts at `0x5B` and advances after every byte, including across group
boundaries:

```
k0 = 0x5B
k_{n+1} = (k_n * 31 + 17) mod 256
```

So the dump hands you five 64-bit constants, not a string. Recovering the flag
takes one more round: unpack each constant little-endian, XOR each byte back
against the same keystream.

```python
k = 0x5B
body = bytearray()
for w in wants:                       # the five immediates, in order
    for i in range(8):
        body.append(((w >> (8 * i)) & 0xFF) ^ k)
        k = (k * 31 + 17) & 0xFF
```

The rolling key is what makes that round necessary rather than cosmetic. A fixed
XOR byte would show up by eye in the repeating structure of the constants. A
rolling one does not, and you have to read the `imul`/`add` out of the dump to
get `31` and `17`.

Body is 40 bytes, exactly five groups. No tail case, no padding.

## 5. Solve

```
$ python3 solve.py chall
[+] stage 2: 388 bytes decrypted
[+] compare immediates: ['0xc5132244c6d6633f', '0x11cfa6c44e4ce484', '0x8e243828decf4968', '0x429989ef0764e4eb', '0xd748357586e47d38']
[+] COMPFEST18{dump_th3_rwx_p4g3_th3n_x0r_1t_b4ck_0nc3!}
[+] re-encrypt matches the immediates

$ echo 'COMPFEST18{dump_th3_rwx_p4g3_th3n_x0r_1t_b4ck_0nc3!}' | ./chall
kunci: mekar
```

`solve.py` takes the static path end to end: symbol lookup, XOR, regex the
`movabs` immediates (`48 b8` / `48 b9` followed by eight bytes), undo the rolling
key. It then re-encrypts its own answer and asserts it reproduces the immediates,
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
than an array. It is also why `GROUP` is a macro: written as a loop over a
constant array it would land in `.rodata` and take a relocation with it.

One flag beyond the specified set was needed: `-fno-asynchronous-unwind-tables`.
Without it gcc emits `.eh_frame`, which carries one `R_X86_64_PC32` against
`.text`. That relocation is harmless in practice, since
`objcopy --only-section=.text` throws `.eh_frame` away, but it makes
`readelf -r` non-empty and the step-2 assertion unsatisfiable.

## 7. Layout

```
./
  challenge.yml      CTFd metadata
  README.md          author-facing
public/
  kepompong.zip      password-protected player distribution (chall + player README)
src/
  chall.c  stage2.c  build.sh  Dockerfile.build  chall  README.player.md
writeup/
  solve.py  README.md  readelf-stage2.txt
```
