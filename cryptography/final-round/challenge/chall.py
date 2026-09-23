#!/usr/bin/env python3
from Crypto.Util.number import getPrime, bytes_to_long, long_to_bytes
from secret import FLAG, generate_primes

p, q = generate_primes(512)

n = p * q
e = 65537

m = bytes_to_long(FLAG)
c = pow(m, e, n)

print(f"n = {n}")
print(f"e = {e}")
print(f"c = {c}")
