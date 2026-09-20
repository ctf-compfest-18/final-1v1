from Crypto.Util.number import getPrime, isPrime

pq = 412023436986659543855531365332575948179811699844327982845455626433876445565248426198098870423161841879261420247188869492560931776375033421130982397485150944909106910269861031862704114880866970564902903653658867433731720813104105190864254793282601391257624033946373269391
e = 65537

while True:
    r = getPrime(128)
    s = r + getPrime(73) + 1
    if isPrime(s) and (r - 1) % e and (s - 1) % e:
        break

rs = r * s
n = pq * rs
with open("flag.txt", "rb") as f:
    flag = f.read().strip()

m = int.from_bytes(flag, "big")
if m >= n:
    raise ValueError("Flag too large")

c = pow(m, e, n)

with open("output.txt", "w") as f:
    f.write(f"pq = {pq}\nrs = {rs}\nn = {n}\ne = {e}\nc = {c}\n")
