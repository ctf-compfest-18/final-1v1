# Neraca
by demtcsre

---

## Flag
```
COMPFEST18{z3_c0z_wHY_nOT??}
```

## Zip Password
```
cf18-neraca
```

## Description
Neraca tua di gudang arsip, kuningannya sudah menghitam. Cuma ada satu
posisi di mana semua lengannya mau diam. Katanya dulu pernah ada yang sempat
menemukannya, tapi catatannya ikut hilang waktu gudangnya pindah.

## Difficulty
medium

## Tags
rev, z3, smt

## Hints
- **Initial:**
  ```
  16 huruf, 6 persamaan. Gak ada yang bisa dipecahin sendirian.
  ```
- **10th minute:**
  ```
  z3-solver. 16 BitVec 8-bit, masukin persamaannya apa adanya.
  ```
- **15th minute:**
  ```
  Constrain ke range 32-126.
  ```

## Deployment
- How to compile (CWD is /src):
```
make
```
- How to run:
```
./chall
```

Reproducible build against the pinned base image (CWD is repo root):
```
docker build -f src/Dockerfile.build -t neraca-build src
```

## Constraints
`x[0..15]` are the 16 bytes between `COMPFEST18{` and `}`. All arithmetic is
`uint32_t`. Six equations, all of which must hold:

```
e1: 64^4*x4  + 64^3*x1  + 64^2*x2  + 64*x0  + x3  ==  819072739
e2: 64^4*x4  + 64^3*x7  + 64^2*x5  + 64*x6  + x8  ==  837007368
e3: 64^4*x11 + 64^3*x9  + 64^2*x8  + 64*x10 + x12 == 1869125647
e4: 64^4*x13 + 64^3*x12 + 64^2*x0  + 64*x15 + x14 == 1430499327
e5: 64^4*x15 + 64^3*x5  + 64^2*x9  + 64*x13 + x2  == 1089316191
e6: x1 ^ x3 ^ x7 ^ x11 ^ x14                      ==        118
```

Weights written out: `16777216, 262144, 4096, 64, 1`. All five ADD equations use
the same base, so there is one weight ladder to read instead of four different
ones. The right-hand sides as they appear in the disassembly:

```
cmp DWORD PTR [rbp-0x6c],0x30d20ee3      #  819072739
cmp DWORD PTR [rbp-0x68],0x31e3b808      #  837007368
cmp DWORD PTR [rbp-0x64],0x6f68980f      # 1869125647
cmp DWORD PTR [rbp-0x60],0x5543afff      # 1430499327
cmp DWORD PTR [rbp-0x5c],0x40eda55f      # 1089316191
cmp DWORD PTR [rbp-0x58],0x76            #        118
```

At `-O0` gcc emits each ADD equation as a Horner chain of `shl eax,0x6` and
`add`, so there are no multiplier constants to copy at all. Only the six
right-hand sides need transcribing.

Five ADD equations, one XOR equation, five bytes each. Byte coverage is
unchanged from the previous weight set: nine bytes appear in two ADD equations,
seven appear in one, and five of those seven are pinned by `e6`. That overlap is
what makes the system uniquely solvable.

## Notes
- SHA256 of both distributed artifacts:
  ```
  chall            45b5dbcf6b443d049d45887979e58a963ef7141231fa8545cc79a45719be1855
  dist-neraca.zip  31d51fd5c65122b1a94564cc397f4c1acaa379bfad6afc6c20a5fe97259c1781
  ```
