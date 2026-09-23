#!/usr/bin/env sage
"""
Varnish - official solver   (SageMath)

    $ sage solve.sage

Stage 1  the diophantine  ->  n = 12*a^3 + b, and one factor of n is  u + 2a
Stage 2  240 low bits of d  ->  low bits of p  ->  Coppersmith  ->  p, q
Stage 3  divisors of n  ->  u, v  ->  x, y  ->  strip the mask off m
"""
import re, time
from pathlib import Path

# ----------------------------------------------------------------- input ----
txt = (Path(__file__).resolve().parent.parent / "challenge" / "output.txt").read_text()
e     = Integer(re.search(r"^e = (\d+)",            txt, re.M).group(1))
n     = Integer(re.search(r"^n = p \* q = (\d+)",   txt, re.M).group(1))
c     = Integer(re.search(r"e, n\) = (\d+)",        txt, re.M).group(1))
bits  = re.search(r"^d = 0b1\[REDACTED\]([01]+)",   txt, re.M).group(1)
a, b  = (Integer(v) for v in re.search(r"^x\*\*3.*?- (\d+)\*\(x\*\*2 \+ y\*\*2\) = (\d+)", txt, re.M).groups())

L     = len(bits)                 # 240 leaked bits
d_low = Integer(bits, base=2)
mod   = 2**L

# ------------------------------------------------- stage 1: the identity ----
# x^3+y^3+4xy(x+y)-a(x^2+y^2) = b   with u=x+y, v=xy   becomes   u^3+uv-a(u^2-2v) = b
#   =>  v*(u + 2a) = -u^3 + a*u^2 + b
#   =>  v = -u^2 + 3au - 6a^2 + (12a^3 + b)/(u + 2a)
# so (u + 2a) | 12a^3 + b   ... and that number is exactly n.
print(f"[*] n == 12*a^3 + b ?  {n == 12*a**3 + b}")
assert n == 12*a**3 + b

# --------------------------------------- stage 2: partial key exposure ------
# e*d = 1 + k*phi,  phi = n - p - q + 1,  pq = n   =>   k*p^2 + (e*d - kn - k - 1)*p + k*n = 0
# The relation survives mod 2^L with d -> d_low, so lift its roots bit by bit.
def roots_mod_2L(k):
    A, B, C = k, e*d_low - k*n - k - 1, k*n
    f = lambda t: A*t*t + B*t + C
    cands = [1] if f(1) % 2 == 0 else []          # p is odd
    for i in range(1, L):
        m2, nxt = 1 << (i+1), []
        for t in cands:
            if f(t) % m2 == 0:            nxt.append(t)
            if f(t + (1<<i)) % m2 == 0:   nxt.append(t + (1<<i))
        cands = nxt
        if not cands:
            break
    return cands

# p = u + 2a with u ~ x+y ~ a  =>  p is a ~302-bit factor of a 906-bit n  =>  beta ~ 1/3
F.<z> = PolynomialRing(Zmod(n))
def coppersmith(r):
    """p = r + 2^L * z0 with z0 small; recover it."""
    for root in (2**L * z + r).monic().small_roots(X=2**66, beta=0.33, epsilon=0.03):
        g = gcd(Integer(2**L*Integer(root) + r), n)
        if 1 < g < n:
            return g
    return None

t0, p = time.time(), None
for k in range(1, e + 1):
    cands = roots_mod_2L(k)
    # Vieta: the two true residues p,q mod 2^L multiply to n mod 2^L
    keep = sorted({v for v in cands for w in cands if v*w % mod == n % mod})
    for r in keep:
        p = coppersmith(r)
        if p:
            print(f"[+] k = {k}, p mod 2^{L} = {r}")
            break
    if p:
        break
    if k % 25 == 0:
        print(f"    ... k = {k}   ({time.time()-t0:.0f}s)")

assert p and n % p == 0
q = n // p
print(f"[+] factored in {time.time()-t0:.1f}s")
print(f"[+] p ({p.nbits()} bits) = {p}")
print(f"[+] q ({q.nbits()} bits) = {q}")

# --------------------------------------------- stage 3: solve for x, y ------
sol = None
for divisor in (1, p, q, n):
    u = divisor - 2*a
    if u <= 0:
        continue
    num = -u**3 + a*u**2 + b
    if num % divisor:
        continue
    v = num // divisor
    disc = u*u - 4*v
    if v <= 0 or disc < 0 or not Integer(disc).is_square():
        continue
    s = Integer(disc).isqrt()
    x, y = (u + s)//2, (u - s)//2
    if x**3 + y**3 + 4*x*y*(x+y) - a*(x**2+y**2) == b:
        sol = (x, y)
        print(f"[+] u + 2a = {'p' if divisor == p else 'q' if divisor == q else divisor}")
        print(f"[+] u = x + y = {u}\n[+] v = x * y  = {v}")
        break
assert sol
x, y = sol

# ------------------------------------------------------- stage 4: flag ------
d   = inverse_mod(e, (p-1)*(q-1))
res = Integer(pow(c, d, n))
from Crypto.Util.number import long_to_bytes
# the equation is symmetric in x and y, but the mask  x**2 + m + y  is not:
# only one of the two orientations strips it cleanly.
for xx, yy in ((x, y), (y, x)):
    m = res - xx*xx - yy
    if m <= 0:
        continue
    flag = long_to_bytes(int(m))
    if b"COMPFEST" in flag:
        print(f"[+] x = {xx}\n[+] y = {yy}")
        print(f"\n[!] FLAG: {flag.decode()}")
        break
