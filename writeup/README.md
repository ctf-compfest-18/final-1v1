# Official Writeup — No Time to Prime

The challenge is intentionally a short three-stage chain. Every stage can be solved with ordinary Python modular arithmetic; no SageMath, lattice reduction, or brute force is required.

## Stage 1 — shared-prime RSA

The two RSA moduli `n1` and `n2` share one prime factor. Compute:

```python
p = gcd(n1, n2)
q1 = n1 // p
phi = (p - 1) * (q1 - 1)
d = pow(e, -1, phi)
m = pow(c1, d, n1)
```

The plaintext is an ASCII token beginning with `NTTP1:`. This token is required to unmask the second ciphertext in Stage 2.

## Stage 2 — common modulus

`c_a` and the recovered `c_b` encrypt the same plaintext under the same modulus but with coprime exponents `e_a` and `e_b`.

First recover `c_b` using the Stage 1 token and the same SHAKE-256 mask shown in `chall.py`. Then find Bézout coefficients `x,y` such that:

```text
x*e_a + y*e_b = 1
```

Recover the plaintext with:

```python
m = c_a^x * c_b^y mod n
```

For a negative exponent, invert the ciphertext modulo `n` first. The plaintext is `NTTP2:<b>`.

## Stage 3 — affine-related ECDSA nonces

The source shows the relation:

```text
k2 = a*k1 + b (mod N)
```

For ECDSA:

```text
s1*k1 = z1 + r1*d  (mod N)
s2*k2 = z2 + r2*d  (mod N)
```

Let:

```text
t = r2 * r1^-1 mod N
```

Substitute the first equation into the second:

```text
(s2*a - t*s1) * k1 = z2 - t*z1 - s2*b  (mod N)
```

So:

```python
k1 = (z2 - t*z1 - s2*b) * inverse(s2*a - t*s1, N) % N
d  = (s1*k1 - z1) * inverse(r1, N) % N
```

Finally use `d` with the SHAKE-256 stream construction in `chall.py` to decrypt `flag_ct`.

