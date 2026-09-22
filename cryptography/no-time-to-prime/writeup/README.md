# No Time to Prime

## Shared prime

Compute `p = gcd(n, peer_n)`, then `q = n // p` and
`d = inverse(e, (p - 1) * (q - 1))`. Decrypt the ciphertext with RSA-OAEP,
SHA-256 and the supplied `oaep_label` to recover the first token.

## Partial prime

The upper 352 bits of a 512-bit prime are known:

```python
p0 = int(p_msb, 16) << 160
R = PolynomialRing(Zmod(n), "x", implementation="NTL")
x = R.gen()
roots = (p0 + x).small_roots(X=2**160, beta=0.49, epsilon=0.04)
```

Select the root for which `p0 + root` divides `n`. Recover the private
exponent and decrypt the second token with RSA-OAEP.

## Partial nonce

For each signature, `s_i*k_i = h_i + r_i*d (mod q)`, where `q` is
the secp256k1 subgroup order. Set:

```text
a_i = r_i / s_i mod q
b_i = h_i / s_i mod q
B   = 2^128
K_i = k_msb_i * B
c_i = K_i + B/2
t_i = (b_i - c_i) mod q
```

Then `a_i*d + b_i - c_i - z_i*q = e_i`, with `-B/2 <= e_i < B/2`.
Use the following integer row basis for the eight signatures:

```text
[ q²     0    ...    0      0      0  ]
[  0    q²    ...    0      0      0  ]
[                  ...               ]
[  0     0    ...   q²      0      0  ]
[ a1*q  a2*q  ...  a8*q    B      0  ]
[ t1*q  t2*q  ...  t8*q    0     B*q ]
```

Run LLL with `delta=0.99`. A row ending in `B*q` gives
`d = (row[-2] // B) % q`. Negate rows ending in `-B*q` first.
Check the candidate against the public key, signatures and nonce prefixes.

Derive the token key as
`SHA256(b"NTTP/ecdsa-key/v1\x00" + d.to_bytes(32, "big"))`,
then decrypt `token_box` with AES-GCM. Its AAD is
`("NTTP/" + instance_id + "/module3").encode("ascii")`.

## Final vault

Concatenate the three raw 32-byte tokens in module order. Apply HKDF-SHA256
with the manifest salt, 32-byte output and info `NTTP/final/v1/<instance_id>`.
Decrypt `final.enc.json` with AES-GCM and AAD `NTTP/<instance_id>/final`.

Run the solver from this directory:

```sh
sage -python ../src/probset/solver/solve_all.py
```
