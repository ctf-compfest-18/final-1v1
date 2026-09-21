#!/usr/bin/env python3
# REV 2 - Neraca.  Six equations, sixteen unknowns, one z3 query.
#   pip install z3-solver && python3 solve.py
from z3 import *

x = [BitVec(f'x{i}', 8) for i in range(16)]
X = [ZeroExt(24, v) for v in x]          # 32-bit, same width the binary computes in

s = Solver()
for v in x:                               # printable ASCII, nothing else assumed
    s.add(UGE(v, 0x20), ULE(v, 0x7e))

s.add(13845841*X[4]  + 226981*X[1]  + 3721*X[2]  + 61*X[0]  + X[3]  == 676537435)
s.add(20151121*X[4]  + 300763*X[7]  + 4489*X[5]  + 67*X[6]  + X[8]  == 1003598700)
s.add(25411681*X[11] + 357911*X[9]  + 5041*X[8]  + 71*X[10] + X[12] == 2827508765)
s.add(28398241*X[13] + 389017*X[12] + 5329*X[0]  + 73*X[15] + X[14] == 2416839387)
s.add(28398241*X[15] + 389017*X[5]  + 5329*X[9]  + 73*X[13] + X[2]  == 1837029765)
s.add(x[1] ^ x[3] ^ x[7] ^ x[11] ^ x[14] == 118)

import time
t = time.time()
assert s.check() == sat
body = bytes(s.model()[v].as_long() for v in x)
print(f"[+] sat in {(time.time()-t)*1000:.0f} ms")
print(f"[+] COMPFEST18{{{body.decode()}}}")

# the model is the flag only if it is the ONLY model - prove it
s.add(Or([x[i] != body[i] for i in range(16)]))
t = time.time()
r = s.check()
print(f"[+] second solution: {r} (in {(time.time()-t)*1000:.0f} ms) -> "
      f"{'unique' if r == unsat else 'NOT UNIQUE'}")
