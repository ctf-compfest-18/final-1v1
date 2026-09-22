# Rolling Shutter

by fele

---

## Flag

```
COMPFEST18{y0ur_p1x3ls_c4nt_h1d3_b3h1nd_l1n34r_m4th}
```

## Description
London Bridge is falling down,
Falling down, falling down.
London Bridge is falling down,
My fair lady.

## Difficulty
Tingkat kesulitan soal: easy

## Hints
* Sixteen known bytes reveal four consecutive generator outputs and then subtract two recurrence equations to eliminate the increment
* hint
* hint dst.

## Tags
xor, lcg

## Deployment
Penjelasan cara menjalankan service yang dibutuhkan serta requirementsnya.

#### Contoh 1
- Install docker engine>=19.03.12 and docker-compose>=1.26.2.
- Run the container using:
    ```
    docker-compose up --build --detach
    ```

#### Contoh 2
- How to compile:
    ```
    gcc soal.c -o soal -O2 -D\_FORTIFY\_SOURCE=2 -fstack-protector-all -Wl,-z,now,-z,relro -Wall -no-pie
    ```
- Jalankan:
    ```
    ./soal
    ```
- Workdir di `/home/...`
- Gunakan libc 2.31 ketika sudah keluar. Alias Ubuntu 20.04.

## Notes
Tambahan informasi untuk soal, deployment, atau serangan yang mungkin terjadi pada service soal
