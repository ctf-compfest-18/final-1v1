from secrets import randbits
from math import gcd
from Crypto.Util.number import getPrime, isPrime, bytes_to_long


def get_primes():
    p = getPrime(1024)
    offset = (1 << 519) | randbits(519)
    q = 7 * p + 2 * offset

    while not isPrime(q):
        q += 2

    return p, q


with open("flag.txt", "rb") as f:
    flag = f.read().strip()

m = bytes_to_long(flag)
e = 65537

while True:
    p, q = get_primes()
    if gcd(e, (p - 1) * (q - 1)) == 1:
        break

n = p * q
assert 0 < m < n
c = pow(m, e, n)

with open("output.txt", "w") as f:
    f.write(f"n = {n}\n")
    f.write(f"e = {e}\n")
    f.write(f"c = {c}\n")
