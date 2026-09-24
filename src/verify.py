#!/usr/bin/env python3
from pathlib import Path
from solve import solve

here = Path(__file__).resolve().parent
expected = (here / 'flag.txt').read_bytes().strip()
got = solve(here / 'output.txt')
assert got == expected, (got, expected)
print('[OK] end-to-end solve verified')
