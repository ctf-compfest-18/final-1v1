#!/usr/bin/env python3
from z3 import *
import time

x = [BitVec(f'x{i}', 8) for i in range(16)]
X = [ZeroExt(24, v) for v in x]

s = Solver()
for v in x:
    s.add(UGE(v, 0x20), ULE(v, 0x7e))

B = 64
s.add(B**4*X[4]  + B**3*X[1]  + B**2*X[2]  + B*X[0]  + X[3]  == 819072739)
s.add(B**4*X[4]  + B**3*X[7]  + B**2*X[5]  + B*X[6]  + X[8]  == 837007368)
s.add(B**4*X[11] + B**3*X[9]  + B**2*X[8]  + B*X[10] + X[12] == 1869125647)
s.add(B**4*X[13] + B**3*X[12] + B**2*X[0]  + B*X[15] + X[14] == 1430499327)
s.add(B**4*X[15] + B**3*X[5]  + B**2*X[9]  + B*X[13] + X[2]  == 1089316191)
s.add(x[1] ^ x[3] ^ x[7] ^ x[11] ^ x[14] == 118)

t = time.time()
assert s.check() == sat
body = bytes(s.model()[v].as_long() for v in x)
print(f"[+] sat in {(time.time()-t)*1000:.0f} ms")
print(f"[+] COMPFEST18{{{body.decode()}}}")

s.add(Or([x[i] != body[i] for i in range(16)]))
t = time.time()
r = s.check()
print(f"[+] second solution: {r} (in {(time.time()-t)*1000:.0f} ms) -> "
      f"{'unique' if r == unsat else 'NOT UNIQUE'}")
