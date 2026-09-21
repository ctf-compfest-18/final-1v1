#!/usr/bin/env python3
"""Recover the RSA token from a partial prime."""
import argparse
from pathlib import Path
from sage.all import PolynomialRing, Zmod
from common import DEFAULT_CHALLENGE, checked, read_json, rsa_token

def recover_factor(obj):
    n = int(obj["n"], 16)
    unknown_bits = obj["unknown_bits"]
    p0 = int(obj["p_msb"], 16) << unknown_bits
    ring = PolynomialRing(Zmod(n), "x", implementation="NTL")
    x = ring.gen()
    f = x + p0
    # beta < .5 covers either balanced 512-bit factor, including p < sqrt(N).
    roots = f.small_roots(X=2**unknown_bits, beta=0.49, epsilon=0.04)
    for root in roots:
        p = p0 + int(root)
        if 1 < p < n and n % p == 0:
            return p
    raise RuntimeError("No factor recovered; use SageMath and the default parameters.")

def solve(challenge=DEFAULT_CHALLENGE):
    obj = read_json(Path(challenge) / "module2.json")
    return checked(challenge, "module2", rsa_token(obj, recover_factor(obj)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenge", type=Path, default=DEFAULT_CHALLENGE)
    print(solve(parser.parse_args().challenge))
