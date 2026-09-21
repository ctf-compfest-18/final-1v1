# Neraca — REV 2, z3 constraint crackme

**Category:** Reverse Engineering · **Difficulty:** medium
**Flag:** `COMPFEST18{z3_c0z_wHY_nOT??}`

---

## 1. What the binary does

`chall` is a stripped, dynamically linked, `-O0` x86-64 ELF. It reads one line,
checks the wrapper, then evaluates six expressions over the 16 bytes inside it.

```
$ file chall
ELF 64-bit LSB pie executable, x86-64, dynamically linked, stripped

$ strings chall | grep -iE 'COMPFEST|kunci|seimbang|timpang'
kunci:
COMPFEST18{
timpang
seimbang
```

No VM, no dispatch loop, no obfuscation. The whole check is straight-line
arithmetic, which is the point: the work is transcribing it correctly, not
fighting the binary.

## 2. Reading the constraints

`-O0` keeps every multiply as a literal `imul`:

```
$ objdump -d -M intel chall | grep -oE 'imul +e[a-z]+,e[a-z]+,0x[0-9a-f]+' | sort -u
imul eax,eax,0xe89         # 3721     = 61^2
imul eax,eax,0x376a5       # 226981   = 61^3
imul edx,eax,0xd34551      # 13845841 = 61^4
imul edx,eax,0x3d          # 61
imul eax,eax,0x1189        # 4489     = 67^2
imul eax,eax,0x496db       # 300763   = 67^3
imul edx,eax,0x1337b51     # 20151121 = 67^4
imul edx,eax,0x43          # 67
imul eax,eax,0x13b1        # 5041     = 71^2
imul eax,eax,0x57617       # 357911   = 71^3
imul edx,eax,0x183c061     # 25411681 = 71^4
imul edx,eax,0x47          # 71
imul eax,eax,0x14d1        # 5329     = 73^2
imul eax,eax,0x5ef99       # 389017   = 73^3
imul edx,eax,0x1b152a1     # 28398241 = 73^4
```

Four bases: 61, 67, 71, 73. Note what is missing from that list: there is no
`imul ...,0x49`. gcc emits `*73` as `shl 3 / add / shl 3 / add`, which is
`((x*8)+x)*8+x`. Miss that and two of the six equations come out wrong.

The right-hand sides are the six `cmp` immediates:

```
cmp DWORD PTR [rbp-0x6c],0x2853245b     # 676537435
cmp DWORD PTR [rbp-0x68],0x3bd1b36c     # 1003598700
cmp DWORD PTR [rbp-0x64],0xa8885c1d     # 2827508765
cmp DWORD PTR [rbp-0x60],0x900e0adb     # 2416839387
cmp DWORD PTR [rbp-0x5c],0x6d7ed985     # 1837029765
cmp DWORD PTR [rbp-0x58],0x76           # 118
```

The 16 unknowns sit in consecutive dword slots, `rbp-0xac` down to `rbp-0x70`
in steps of 4, in declaration order:

```
x0 =-0xac  x1 =-0xa8  x2 =-0xa4  x3 =-0xa0  x4 =-0x9c  x5 =-0x98  x6 =-0x94  x7 =-0x90
x8 =-0x8c  x9 =-0x88  x10=-0x84  x11=-0x80  x12=-0x7c  x13=-0x78  x14=-0x74  x15=-0x70
```

Mapping each `mov eax,[rbp-0x..]` through that table gives the system:

```
e1: 13845841*x4  + 226981*x1  + 3721*x2  + 61*x0  + x3  == 676537435
e2: 20151121*x4  + 300763*x7  + 4489*x5  + 67*x6  + x8  == 1003598700
e3: 25411681*x11 + 357911*x9  + 5041*x8  + 71*x10 + x12 == 2827508765
e4: 28398241*x13 + 389017*x12 + 5329*x0  + 73*x15 + x14 == 2416839387
e5: 28398241*x15 + 389017*x5  + 5329*x9  + 73*x13 + x2  == 1837029765
e6: x1 ^ x3 ^ x7 ^ x11 ^ x14                            == 118
```

Six equations, sixteen unknowns, all `uint32_t`.

## 3. Why brute force fails and z3 does not

The flag body is 16 printable bytes. `95^16` is about `4.4e31`, roughly
`2^105`. At a billion candidates per second that is `1.4e15` years. Nothing
about the oracle changes that, which is why the binary does not bother with
fail-fast behaviour: there is no timing signal worth protecting.

Per-byte search does not help either, and that is the deliberate part. No
equation involves fewer than five bytes, and no byte can be isolated:

- `x0` appears in `e1` and `e4`, `x2` in `e1` and `e5`, `x4` in `e1` and `e2`,
  `x5` in `e2` and `e5`, `x8` in `e2` and `e3`, `x9` in `e3` and `e5`,
  `x12` in `e3` and `e4`, `x13` in `e4` and `e5`, `x15` in `e4` and `e5`.
- The seven bytes that appear in only one ADD equation are `x1, x3, x6, x7,
  x10, x11, x14`, and five of those are exactly the XOR group in `e6`.

So there is no equation you can solve alone and substitute forward. Guess one
byte and you learn nothing until four more in the same equation are also right.

z3 does not care. Six linear constraints over 16 bounded integers is a small
query: the ADD equations are positional sums the bit-blaster propagates digit
by digit, and the printable-ASCII bound cuts each byte to 95 values. It returns
in **141 ms**.

## 4. Uniqueness

A model is only the flag if it is the *only* model. Worth checking, because six
equations over sixteen unknowns is underdetermined in the naive counting sense
(`6 < 16`), and a careless weight set really does admit several printable
solutions. This one does not:

```
[+] sat in 141 ms
[+] COMPFEST18{z3_c0z_wHY_nOT??}
[+] second solution: unsat (in 289 ms) -> unique
```

Adding `Or(x[i] != model[i])` and re-solving returns `unsat`, so the printable
solution is unique and any correct z3 script lands on the flag.

The weight structure is what makes that work. Each ADD equation is a positional
sum in base 61, 67, 71 or 73, and every one of those bases is smaller than the
width of the printable range (95). So a single equation on its own does admit
several printable readings: add one to a digit, subtract the base from the
next, same total. Overlap kills those. Any such shift moves two bytes at once,
and nine of the sixteen bytes are covered by a second ADD equation with a
different weight while five more are covered by `e6`, so the shift always
breaks something else.

## 5. Solve

See `solve.py`.

```python
x = [BitVec(f'x{i}', 8) for i in range(16)]
X = [ZeroExt(24, v) for v in x]          # 32-bit, the width the binary uses
s = Solver()
for v in x:
    s.add(UGE(v, 0x20), ULE(v, 0x7e))    # printable ASCII
s.add(13845841*X[4] + 226981*X[1] + 3721*X[2] + 61*X[0] + X[3] == 676537435)
...
s.add(x[1] ^ x[3] ^ x[7] ^ x[11] ^ x[14] == 118)
```

```
$ python3 solve.py
[+] sat in 141 ms
[+] COMPFEST18{z3_c0z_wHY_nOT??}
[+] second solution: unsat (in 289 ms) -> unique

$ echo 'COMPFEST18{z3_c0z_wHY_nOT??}' | ./chall
kunci: seimbang
```

## 6. Layout

```
./
  challenge.yml      CTFd metadata
  README.md          author-facing
  neraca.zip         password-protected player distribution
src/
  chall.c  chall  Makefile  Dockerfile.build
public/
  chall  README.md
writeup/
  solve.py  README.md
```
