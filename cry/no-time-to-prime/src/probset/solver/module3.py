#!/usr/bin/env python3
"""Recover the ECDSA key from partial nonces."""
import argparse
import hashlib
from pathlib import Path
from sage.all import EllipticCurve, GF, Matrix, ZZ
from common import DEFAULT_CHALLENGE, checked, read_json
from app.crypto_core import aad, module3_key, unseal

def public_curve(obj):
    c = obj["curve"]
    E = EllipticCurve(GF(int(c["p"], 16)), [int(c["a"], 16), int(c["b"], 16)])
    G = E(int(c["gx"], 16), int(c["gy"], 16))
    Q = E(int(obj["public_key"]["x"], 16), int(obj["public_key"]["y"], 16))
    return E, G, Q, int(c["order"], 16)

def recover_private(obj):
    _, G, Q, q = public_curve(obj)
    B = 1 << obj["nonce_unknown_bits"]
    signatures = obj["signatures"]
    count = len(signatures)
    lattice = Matrix(ZZ, count + 2, count + 2)
    for i, sig in enumerate(signatures):
        r, s = int(sig["r"], 16), int(sig["s"], 16)
        h = int.from_bytes(hashlib.sha256(bytes.fromhex(sig["message_hex"])).digest(), "big")
        a = r * pow(s, -1, q) % q
        b = h * pow(s, -1, q) % q
        center = (int(sig["k_msb"], 16) << obj["nonce_unknown_bits"]) + B // 2
        lattice[i, i] = q * q
        lattice[count, i] = a * q
        lattice[count + 1, i] = ((b - center) % q) * q
    lattice[count, count] = B
    lattice[count + 1, count + 1] = B * q
    reduced = lattice.LLL(delta=0.99)
    for row in reduced.rows():
        if abs(row[-1]) != B * q:
            continue
        # The short vector or its negative encodes the same private key.
        sign = 1 if row[-1] > 0 else -1
        if row[-2] % B:
            continue
        d = int(sign * row[-2] // B) % q
        if d and d * G == Q:
            # Check all leaks and signatures, not just the AES tag.
            for sig in signatures:
                r, s = int(sig["r"], 16), int(sig["s"], 16)
                h = int.from_bytes(hashlib.sha256(bytes.fromhex(sig["message_hex"])).digest(), "big")
                k = (h + r*d) * pow(s, -1, q) % q
                if not k or k >> obj["nonce_unknown_bits"] != int(sig["k_msb"], 16):
                    raise ValueError("Nonce leak mismatch")
                if int((k * G)[0]) % q != r:
                    raise ValueError("Invalid ECDSA signature")
            return d
    raise RuntimeError("LLL failed to recover the public key; do not distribute this instance.")

def solve(challenge=DEFAULT_CHALLENGE):
    obj = read_json(Path(challenge) / "module3.json")
    d = recover_private(obj)
    token = unseal(module3_key(d), obj["token_box"], aad(obj["instance_id"], "module3"))
    return checked(challenge, "module3", token.hex())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenge", type=Path, default=DEFAULT_CHALLENGE)
    print(solve(parser.parse_args().challenge))
