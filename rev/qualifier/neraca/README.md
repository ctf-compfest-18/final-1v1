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
e1: 13845841*x4  + 226981*x1  + 3721*x2  + 61*x0  + x3  == 676537435
e2: 20151121*x4  + 300763*x7  + 4489*x5  + 67*x6  + x8  == 1003598700
e3: 25411681*x11 + 357911*x9  + 5041*x8  + 71*x10 + x12 == 2827508765
e4: 28398241*x13 + 389017*x12 + 5329*x0  + 73*x15 + x14 == 2416839387
e5: 28398241*x15 + 389017*x5  + 5329*x9  + 73*x13 + x2  == 1837029765
e6: x1 ^ x3 ^ x7 ^ x11 ^ x14                            == 118
```

Five ADD equations, one XOR equation, five bytes each. The ADD weights are
powers of 61, 67, 71 and 73. Byte coverage is deliberate: nine bytes appear in
two ADD equations, seven appear in one, and five of those seven are pinned by
`e6`. That overlap is what makes the system uniquely solvable.
