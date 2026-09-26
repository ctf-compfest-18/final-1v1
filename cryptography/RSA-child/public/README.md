# RSA-child

by fele

---

## Flag

```
COMPFEST18{4_ch4ng3_0f_sc4l3_br1ngs_th3_pr1m3s_b4ck_t0g3th3r_h3h3h3_c0ngr4atZzz}
```

## Description
You know what a man-child is, and you know what a woman-child is. You should already know what an RSA-child is.

## Difficulty
Tingkat kesulitan soal: easy

## Hints
* The primes may look far apart, but multiplying the modulus by a specific small constant changes everything.
* Once multiplied correctly, the gap between the factors becomes small enough to easily break using Fermat's Factorization.
* hint dst.

## Tags
rsa, math, fermat factorization

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
