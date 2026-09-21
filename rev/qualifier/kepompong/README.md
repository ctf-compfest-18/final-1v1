# Kepompong
by demtcsre

---

## Flag
```
COMPFEST18{dump_th3_rwx_p4g3_th3n_x0r_1t_b4ck_0nc3!}
```

## Zip Password
```
cf18-kepompong
```

## Description
Berkasnya kecil. Bongkar isinya dan hampir tidak ada apa-apa di dalam
sana. Programnya tetap jalan, tetap menjawab. Mekar, atau belum.

File-only challenge. No connection info.

## Difficulty
medium

## Tags
rev, self-modifying, mmap, anti-static

## Deployment
- Build (CWD /src): `./build.sh`
- Reproducible build against the pinned base image (CWD /src):
```
docker build -f Dockerfile.build -t kepompong-build .
```

## Stage 2 Parameters
Blob XOR key, 8 bytes, repeating (`KEY[8]` in chall.c):
```
0x9A, 0x47, 0xC3, 0x1E, 0x75, 0xB2, 0x6D, 0x08
```

Check logic inside stage 2: each input byte is XORed against a rolling key,
packed little-endian into 64-bit groups, and each group compared to an
immediate. The rolling key starts at `0x5B` and advances per byte:
```
k = 0x5B
k = (unsigned char)(k * 31 + 17)     after every byte
```
Group immediates, in order:
```
GROUP( 0, 0xC5132244C6D6633F)
GROUP( 8, 0x11CFA6C44E4CE484)
GROUP(16, 0x8E243828DECF4968)
GROUP(24, 0x429989EF0764E4EB)
GROUP(32, 0xD748357586E47D38)
```
Body is 40 bytes, exactly 5 groups, no tail case. There is no `memcmp`: a
dumped page still has to be run through one XOR round before it says anything.

`readelf -r stage2.o`, asserted by step 2 of build.sh:
```
There are no relocations in this file.
```
Transcript in `writeup/readelf-stage2.txt`. Step 1 passes
`-fno-asynchronous-unwind-tables` on top of the specified flags; without it gcc
emits `.eh_frame` with one `R_X86_64_PC32` against `.text`, and the assertion
can never pass.

## Notes
Nothing here
