# Buku Tamu
by demtcsre

---

## Flag
```
COMPFEST18{sr0p_1s_th3_0nly_w4y_0ut_0f_g4dg3t_st4rv4t10n}
```

## Zip Password
```
cf18-buku-tamu
```

## Description
Kantor lama itu sudah kosong bertahun-tahun, tapi buku tamunya masih
tergeletak di meja depan. Tulis namamu, tinggalkan pesan untuk siapa pun yang
datang berikutnya. Penjaganya bersumpah dia membaca semuanya, walaupun belum
ada yang pernah benar-benar melihat dia.

Connect with:
`nc 34.1.203.129 5500`

## Difficulty
medium

## Tags
pwn, srop, sigreturn

## Hints
- **Initial:**
  ```
  Cuma ada satu gadget buat isi register: pop rax. Sisanya numpang lewat satu syscall.
  ```
- **10th minute:**
  ```
  rax=15. Syscall apa itu?
  ```
- **15th minute:**
  ```
  pop rax -> 15 -> syscall gadget -> rt_sigreturn. Susun sigcontext palsu: rax=59, rdi=&"/bin/sh", rsi=0, rdx=0. pwntools SigreturnFrame().
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
  chall               9e93296c31b214de1401c6c05db36837aa818525b065a4e9a73708bee9715bb1
  dist-buku-tamu.zip  81dd356a33a360d6930366ea43484dfbf6918a64b83e9ae053f7af4518726687
  ```