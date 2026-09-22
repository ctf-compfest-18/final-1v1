from math import gcd, isqrt


with open("output.txt") as f:
    values = {}
    for line in f:
        name, value = line.split("=")
        values[name.strip()] = int(value.strip())

n = values["n"]
e = values["e"]
c = values["c"]

# q is close to 7*p, so factor 7*n = (7*p)*q.
target = 7 * n
a = isqrt(target)
if a * a < target:
    a += 1

while True:
    b_squared = a * a - target
    b = isqrt(b_squared)
    if b * b == b_squared:
        break
    a += 1

# Remove the extra multiplier using the original n.
p = gcd(a - b, n)
q = n // p
assert 1 < p < n and p * q == n

phi = (p - 1) * (q - 1)
d = pow(e, -1, phi)
m = pow(c, d, n)

flag = m.to_bytes((m.bit_length() + 7) // 8, "big")
print(flag.decode())
