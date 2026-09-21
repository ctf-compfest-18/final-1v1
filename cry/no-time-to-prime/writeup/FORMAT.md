# Public format v1

Semua bilangan besar di JSON berupa **hex unsigned tanpa `0x`**. `e`, jumlah bit,
dan durasi berupa integer JSON. Hex ciphertext/message harus diparse menjadi byte,
bukan di-hash sebagai string hex. Semua token merupakan 32 byte acak, ditampilkan
sebagai 64 karakter hex (termasuk leading zero). Ketiga token independen.

## Module 1 — RSA shared prime

`n`, `peer_n`, `e`, `peer_e` adalah public keys dua device. `ciphertext` adalah
recovery token yang dienkripsi di bawah `n`. Padding **RSA-OAEP**, hash **SHA-256**,
MGF1-SHA256, label tepat byte ASCII `oaep_label` (tidak kosong).

## Module 2 — RSA partial prime

`n = p*q`. `p` dan `q` masing-masing 512 bit. `p_msb` adalah prefix **p**, bukan q.

```text
p = (int(p_msb, 16) << unknown_bits) + x
0 <= x < 2**unknown_bits
unknown_bits = 160
```

Enkripsi token dan OAEP sama seperti Module 1. `p_msb` berisi 352 bit teratas;
160 bit terbawah tidak tersedia.

## Module 3 — ECDSA partial nonce

Kurva secp256k1 dan generatornya ditulis lengkap dalam `curve`. `order` adalah
order subgroup; berbeda dengan modulus field `p`. Public key `Q = d*G`.

Untuk setiap record:

```text
h = int.from_bytes(SHA256(bytes.fromhex(message_hex)).digest(), 'big')
r = x_coordinate(k*G) mod order
s = inverse(k, order) * (h + r*d) mod order
k = (int(k_msb, 16) << nonce_unknown_bits) + u
0 <= u < 2**nonce_unknown_bits
nonce_unknown_bits = 128
```

Tidak ada low-S normalization. Gunakan nilai `s` apa adanya.
Token dibuka menggunakan:

```python
key = SHA256(b'NTTP/ecdsa-key/v1\x00' + d.to_bytes(32, 'big')).digest()
aad = ('NTTP/' + instance_id + '/module3').encode('ascii')
```

`\x00` di ekspresi bytes Python berarti **satu byte NUL**. `token_box` menggunakan
AES-256-GCM dengan nonce dan tag yang tertulis di JSON; tag 16 byte.
Verifikasi authentication tag wajib dilakukan.

## Commitments dan final vault

SHA-256 commitments bukan token dan tidak boleh dimasukkan sebagai pengganti token:

```python
SHA256(b'NTTP/commit/v1\x00' + instance_id.encode('ascii')
       + b'\x00' + module.encode('ascii') + b'\x00' + raw_token).hexdigest()
```

`module` persis `module1`, `module2`, atau `module3`.

Master key = **HKDF-SHA256**, output 32 byte, salt dari `manifest.kdf.salt`,
info ASCII `NTTP/final/v1/` + instance_id, input key material:

```text
raw_token1 || raw_token2 || raw_token3  (96 byte; jangan gunakan string hex)
```

`final.enc.json` dienkripsi AES-256-GCM; AAD ASCII `NTTP/` + instance_id + `/final`.
Nonce dan tag tidak rahasia. Label, urutan, dan case instance ID harus tepat.
Implementasi format publik ada di `app/crypto_core.py`; `recover.py` menyediakan
recovery client yang bisa digunakan tanpa GUI.
