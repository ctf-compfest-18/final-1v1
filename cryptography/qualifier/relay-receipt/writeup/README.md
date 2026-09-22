# Relay Receipt

## Shared prime

The directory moduli share a prime. Compute `p = gcd(N0, N1)`,
factor `N0`, and recover its private exponent. Decrypt `ticket` and
encode the result as exactly 32 bytes.

For each encrypted layer, the AES-GCM key is
`SHA256(b"relay/" + label + b"\x00" + raw)`, with the label as AAD.
Use label `delivery` and the ticket to open the first layer.

## Common modulus

The delivery contains two encryptions of the same token under one modulus.
Since `65537*32769 - 65539*32768 = 1`:

```python
m = pow(c1, 32769, n) * pow(c2, -32768, n) % n
token = m.to_bytes(32, "big")
```

Open `policy` with the token to obtain `a` and `b`.

## Related nonces

The signatures satisfy `k2 = a*k1 + b (mod n)`, where `n` is the
P-256 subgroup order. Let `z1` and `z2` be the SHA-256 message hashes.
Eliminating the nonces from the two ECDSA equations gives:

```python
D = (a*s2*r1 - s1*r2) % n
T = (s1*z2 - a*s2*z1 - b*s1*s2) % n
d = T * pow(D, -1, n) % n
```

Open `vault` using `d.to_bytes(32, "big")` to recover the flag.

Run the solver from this directory:

```sh
python3 ../src/probset/solve.py ../src/participant
```
