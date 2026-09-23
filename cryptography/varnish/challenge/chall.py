#!/usr/bin/env python3
#
# Varnish :: COMPFEST 18 Final Round
#
# A little polish never hurt anybody. A second coat, however...
#
from Crypto.Util.number import bytes_to_long, isPrime
from secret import FLAG
import random


def genkey(nbit):
    """
    Pick a secret pair (x, y) and hide it inside a cubic diophantine.
    The modulus is built *out of* that same pair, so the equation and the
    key are two views of one secret.
    """
    while True:
        a = (random.getrandbits(nbit) | (1 << (nbit - 1))) & ~1
        u = random.getrandbits(nbit + 2) | (1 << (nbit + 1))

        p = u + 2 * a
        if not isPrime(p):
            continue

        for _ in range(1 << 13):
            x = random.randrange(u // 3, u // 2)
            y = u - x
            v = x * y

            q = v + u**2 - 3 * a * u + 6 * a**2
            if not isPrime(q):
                continue

            b = x**3 + y**3 + 4 * x * y * (x + y) - a * (x**2 + y**2)
            if b < 0:
                continue

            if (p - 1) * (q - 1) % e == 0:
                continue

            return a, b, x, y, p, q


e = 257
a, b, x, y, p, q = genkey(300)

n = p * q
d = pow(e, -1, (p - 1) * (q - 1))
m = bytes_to_long(FLAG)
c = pow(x**2 + m + y, e, n)

leak = 240
lsb = bin(d % 2**leak)[2:].zfill(leak)

print(f'm = bytes_to_long(flag)')
print(f'e = {e}')
print(f'n = p * q = {n}')
print(f'd = 0b1[REDACTED]{lsb}')
print(f'c = pow(x**2 + m + y, e, n) = {c}')
print(f'x**3 + y**3 + 4*x*y*(x + y) - {a}*(x**2 + y**2) = {b}')
