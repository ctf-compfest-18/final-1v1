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

## Hints
- **Initial:**
  ```
  Yang diem di file beda sama yang jalan di memori.
  ```
- **10th minute:**
  ```
  Breakpoint di call ke alamat hasil mmap. Dump page-nya.
  ```
- **15th minute:**
  ```
  XOR biasa, key pendek tetap, satu byte satu byte. Invert aja.
  ```

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

Check logic inside stage 2: a fixed 4-byte repeating key, no advancing state,
one byte compared at a time. Position `i` is checked against key byte `i % 4`:
```
key = 0x5B, 0xA7, 0x3E, 0xC9

if ((in[i] ^ key[i % 4]) != cmp[i]) return 0;
```
The 40 comparison bytes `cmp[0..39]`, in order:
```
  3F D2 53 B9 04 D3 56 FA
  04 D5 49 B1 04 D7 0A AE
  68 F8 4A A1 68 C9 61 B1
  6B D5 61 F8 2F F8 5C FD
  38 CC 61 F9 35 C4 0D E8
```
Body is 40 bytes, one check per byte, fully unrolled with the key bytes and the
comparison bytes as inline literals. No indexed const array, so nothing lands in
`.rodata` and nothing takes a RIP-relative reference.

The key bytes are declared `volatile`. Without that, gcc `-O1` folds
`(in[i] ^ K) != M` into `cmp BYTE PTR [rdi+i], M^K` and the dumped page spells
the flag out in plaintext immediates, which removes the decode round entirely.
With `volatile` the dump shows the key stored to the stack and a real
`xor dl, [rdi+off]` per byte, so recovering the flag still costs one XOR pass.

`readelf -r stage2.o`, asserted by step 2 of build.sh:
```
There are no relocations in this file.
```
Transcript in `writeup/readelf-stage2.txt`. Step 1 passes
`-fno-asynchronous-unwind-tables` on top of the specified flags; without it gcc
emits `.eh_frame` with one `R_X86_64_PC32` against `.text`, and the assertion
can never pass.

## Notes
- SHA256 of both distributed artifacts:
  ```
  chall               98fbbcb5f0383401bdeb764e7eacceffbf664aa140c1cfc864e12438a0046a1d
  dist-kepompong.zip  62983e4488033a7768149de2a16fab0dbcde6a3a095ff9189116321254806d57
  ```
