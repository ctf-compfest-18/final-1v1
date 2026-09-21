#!/usr/bin/env python3
"""Recover the RSA token using a shared prime."""
import argparse
from math import gcd
from pathlib import Path
from common import DEFAULT_CHALLENGE, checked, read_json, rsa_token

def solve(challenge=DEFAULT_CHALLENGE):
    obj = read_json(Path(challenge) / "module1.json")
    n = int(obj["n"], 16)
    p = gcd(n, int(obj["peer_n"], 16))
    return checked(challenge, "module1", rsa_token(obj, p))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenge", type=Path, default=DEFAULT_CHALLENGE)
    print(solve(parser.parse_args().challenge))
