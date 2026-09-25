# Neraca — REV 2, z3 constraint crackme

**Category:** Reverse Engineering · **Difficulty:** medium · **Target time:** 9-13 min
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

At `-O0` nothing is folded, but there are also no multiplier constants to read.
Every ADD equation is a Horner chain of shift-by-6 and add:

```
1390:  mov  eax,DWORD PTR [rbp-0x9c]
1396:  shl  eax,0x6
1399:  mov  edx,eax
139b:  mov  eax,DWORD PTR [rbp-0xa8]
13a1:  add  eax,edx
13a3:  shl  eax,0x6
       ...
13c8:  add  eax,edx
13ca:  mov  DWORD PTR [rbp-0x6c],eax
```

`shl 6` is a multiply by 64, applied four times, so each equation is a base-64
positional sum over five bytes:

```
((((a*64 + b)*64 + c)*64 + d)*64 + e   ==   64^4*a + 64^3*b + 64^2*c + 64*d + e
```

Weights are therefore `16777216, 262144, 4096, 64, 1`, the same ladder in all
five equations. The only constants to transcribe are the six right-hand sides:

```
cmp DWORD PTR [rbp-0x6c],0x30d20ee3      #  819072739
cmp DWORD PTR [rbp-0x68],0x31e3b808      #  837007368
cmp DWORD PTR [rbp-0x64],0x6f68980f      # 1869125647
cmp DWORD PTR [rbp-0x60],0x5543afff      # 1430499327
cmp DWORD PTR [rbp-0x5c],0x40eda55f      # 1089316191
cmp DWORD PTR [rbp-0x58],0x76            #        118
```

The 16 unknowns sit in consecutive dword slots, `rbp-0xac` down to `rbp-0x70`
in steps of 4, in declaration order:

```
x0 =-0xac  x1 =-0xa8  x2 =-0xa4  x3 =-0xa0  x4 =-0x9c  x5 =-0x98  x6 =-0x94  x7 =-0x90
x8 =-0x8c  x9 =-0x88  x10=-0x84  x11=-0x80  x12=-0x7c  x13=-0x78  x14=-0x74  x15=-0x70
```

Mapping each `mov eax,[rbp-0x..]` through that table gives the system:

```
e1: 64^4*x4  + 64^3*x1  + 64^2*x2  + 64*x0  + x3  ==  819072739
e2: 64^4*x4  + 64^3*x7  + 64^2*x5  + 64*x6  + x8  ==  837007368
e3: 64^4*x11 + 64^3*x9  + 64^2*x8  + 64*x10 + x12 == 1869125647
e4: 64^4*x13 + 64^3*x12 + 64^2*x0  + 64*x15 + x14 == 1430499327
e5: 64^4*x15 + 64^3*x5  + 64^2*x9  + 64*x13 + x2  == 1089316191
e6: x1 ^ x3 ^ x7 ^ x11 ^ x14                      ==        118
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
[+] second solution: unsat (in 32 ms) -> unique
```

Adding `Or(x[i] != model[i])` and re-solving returns `unsat`, so the printable
solution is unique and any correct z3 script lands on the flag.

The weight structure is what makes that work. Each ADD equation is a positional
sum in base 64, which is smaller than the width of the printable range (95). So a single equation on its own does admit
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
s.add(64**4*X[4] + 64**3*X[1] + 64**2*X[2] + 64*X[0] + X[3] == 819072739)
...
s.add(x[1] ^ x[3] ^ x[7] ^ x[11] ^ x[14] == 118)
```

```
$ python3 solve.py
[+] sat in 141 ms
[+] COMPFEST18{z3_c0z_wHY_nOT??}
[+] second solution: unsat (in 32 ms) -> unique

$ echo 'COMPFEST18{z3_c0z_wHY_nOT??}' | ./chall
kunci: seimbang
```

## 6. Layout

```
./
  challenge.yml      CTFd metadata
  README.md          author-facing
src/
  chall.c  Makefile  Dockerfile.build    source and build
  chall                                 build output
  README.player.md                      player README, packed into the zip
public/
  dist-neraca.zip    the only thing players get: chall + README.md, no source
writeup/
  solve.py  README.md
```
