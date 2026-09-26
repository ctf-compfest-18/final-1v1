# Ruang Baca
by demtcsre

---

## Flag
```
COMPFEST18{n0_3x3cv3_n0_mm4p_just_0p3n_r34d_wr1t3}
```

## Zip Password
```
cf18-ruang-baca
```

## Description
Ruang arsip disegel sejak audit terakhir. Yang tersisa untuk tamu cuma
meja baca di depan pintu. Petugasnya masih mau memberitahu di mana berkasmu
disimpan, bahkan menyodorkan selembar kertas kosong untuk menyalin. Sisanya
sudah bukan haknya lagi.

Connect with:
`nc 34.1.203.129 5600`

## Difficulty
medium

## Tags
pwn, rop, seccomp, orw

## Hints
- **Initial:**
  ```
  Cek syscall apa yang masih diizinin. Gadgetnya udah ada semua di binary.
  ```
- **10th minute:**
  ```
  seccomp-tools dump. ROPgadget buat pop rdi/rsi/rdx/rax + syscall.
  ```
- **15th minute:**
  ```
  open("/flag.txt",0) -> read(fd,buf,0x80) -> write(1,buf,0x80).
  ```

## Deployment
- How to compile (CWD is /src):
```
make
```
- How to run:
```
docker compose up --build -d
```

## Notes
- SHA256 of both distributed artifacts:
  ```
  chall                d6b121cb4c35908ec9bde3be9905534ff57a9dea3d1adf1eb46ff98f2184223c
  dist-ruang-baca.zip  212c784673af1c199a45bfebfe06447fa3b99005f3614a889594f0d5a70ae031
  ```
