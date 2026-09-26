from math import isqrt
from pathlib import Path

values = {}
output = Path(__file__).resolve().parents[1] / "public" / "output.txt"
for line in output.open(encoding="utf-8"):
    key, value = line.strip().split(" = ")
    values[key] = int(value)

pq, rs, e, c = values["pq"], values["rs"], values["e"], values["c"]
n = pq * rs

p = 636606729769440499166579950236036751749912014371509557713570027508971809534551913252252094954941974952859310861988904737359709200557919
q = 647218161102195448058768698177623951380616936266986989243011933572862870905830904361851542450154852431416136790787107595965374752513489
a = isqrt(rs) + 1

while True:
    b = isqrt(a * a - rs)
    if b * b == a * a - rs:
        r, s = a - b, a + b
        break
    a += 1

assert p * q == pq
assert p * q * r * s == n
d = pow(e, -1, (p - 1) * (q - 1) * (r - 1) * (s - 1))
m = pow(c, d, n)
flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
print(flag.decode())
