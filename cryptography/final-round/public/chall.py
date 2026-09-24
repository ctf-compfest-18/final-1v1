#!/usr/bin/env python3
from Crypto.Util.number import bytes_to_long
from secret import FLAG, generate_primes
import random

p, q = generate_primes(512)

n = p * q
e = 65537

x = random.randrange(p // 10, p // 9)
y = random.randrange(p // 10, p // 9)

alpha = p - (3 * x + y)
beta = q - (2 * x + y)

A = 2 * alpha + 3 * beta
B = alpha + beta
b = 6 * x**2 + 5 * x * y + y**2 + A * x + B * y

m = bytes_to_long(FLAG)
c = pow(x**2 + m + y, e, n)

print(f"n = {n}")
print(f"e = {e}")
print(f"c = pow(x**2 + m + y, e, n) = {c}")
print(f"6*x**2 + 5*x*y + y**2 + {A}*x + {B}*y = {b}")
