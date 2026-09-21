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
- Distributed binary: `public/chall`, sha256
  `dffbbae5158eda41fe6ae7b3761c976ab5b68ffb94af6c7064f18536f5f6351b`.
  The image recompiles from `src/chall.c` with the same pinned flags.
- The flag is baked into the image at build time from `src/flag.txt`.
  Changing it requires `docker compose up --build -d`, not just a restart.
- redpwn jail needs `privileged: true` to set up namespaces. Without it the
  container exits at startup, not at exploit time.
- `JAIL_PORT=5500` is set in the Dockerfile so the jail listens on the port
  compose publishes. The compose file overrides the other `JAIL_*` limits.
- The exploit chain lives entirely inside the no-PIE image, so it is
  libc-version independent. Verified against Ubuntu 22.04 and Kali rolling.
- Intended solve is SROP. Full reasoning, including the one near-miss gadget
  (`mov edi, 0x404058 ; jmp rax`) and why it is dead, is in `writeup/README.md`.
