#!/usr/bin/env python3
"""Generate a challenge instance."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import secrets
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "participant"))
sys.path.insert(0, str(ROOT / "probset" / "solver"))
from sage.all import EllipticCurve, GF
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Util.number import getPrime
from app.crypto_core import MODULES, aad, commitment, derive_master_key, module3_key, read_json, seal

CURVE = {
    "name": "secp256k1",
    "p": "fffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f",
    "a": "0", "b": "7",
    "gx": "79be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798",
    "gy": "483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8",
    "order": "fffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141"
}
PROFILE = {"rsa_prime_bits": 512, "rsa_exponent": 65537, "rsa_unknown_bits": 160,
           "ecdsa_curve": "secp256k1", "nonce_unknown_bits": 128,
           "signature_count": 8, "duration_seconds": 1200,
           "small_roots_beta": 0.49, "small_roots_epsilon": 0.04}

def hx(value):
    return format(int(value), "x")

def dump(path, obj, private=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    if private:
        path.chmod(0o600)

def prime(bits, e, used):
    while True:
        p = getPrime(bits)
        if p not in used and math.gcd(e, p - 1) == 1:
            used.add(p)
            return p

def rsa_box(n, e, token, label):
    key = RSA.construct((n, e))
    cipher = PKCS1_OAEP.new(key, hashAlgo=SHA256, label=label.encode("ascii"))
    return {"n": hx(n), "e": e, "padding": "RSA-OAEP-SHA256", "oaep_label": label,
            "ciphertext": cipher.encrypt(token).hex()}

def build(challenge, private, flag, config):
    if config != PROFILE:
        raise ValueError("Unsupported profile. Keep config.json defaults; recalibrate code/tests before changing parameters.")
    challenge, private = Path(challenge), Path(private)
    challenge.mkdir(parents=True, exist_ok=True)
    private.mkdir(parents=True, exist_ok=True)
    private.chmod(0o700)
    instance_id = secrets.token_hex(16)
    tokens = {m: secrets.token_bytes(32) for m in MODULES}
    manifest = {"format_version": 1, "title": "No Time to Prime", "instance_id": instance_id,
                "duration_seconds": config["duration_seconds"],
                "commitments": {m: commitment(instance_id, m, tokens[m]) for m in MODULES},
                "kdf": {"algorithm": "HKDF-SHA256", "salt": secrets.token_hex(32),
                        "info": "NTTP/final/v1/" + instance_id,
                        "input": "raw token1 || raw token2 || raw token3; 32 bytes each", "length": 32}}
    e, bits = config["rsa_exponent"], config["rsa_prime_bits"]
    used = set()
    p1 = prime(bits, e, used)
    def partner(p):
        while True:
            q = prime(bits, e, used)
            if (p*q).bit_length() == 2*bits and abs(p-q).bit_length() >= bits-16:
                return q
    q1, peer_q = partner(p1), partner(p1)
    p2 = prime(bits, e, used)
    q2 = partner(p2)
    m1 = rsa_box(p1*q1, e, tokens["module1"], "NTTP/" + instance_id + "/module1")
    m1.update(instance_id=instance_id, peer_n=hx(p1*peer_q), peer_e=e,
              incident="Two independently registered RSA devices used the same faulty prime cache.")
    m2 = rsa_box(p2*q2, e, tokens["module2"], "NTTP/" + instance_id + "/module2")
    m2.update(instance_id=instance_id, prime_bits=bits, unknown_bits=config["rsa_unknown_bits"],
              p_msb=hx(p2 >> config["rsa_unknown_bits"]),
              leak_encoding="p = (int(p_msb,16) << unknown_bits) + x; 0 <= x < 2^unknown_bits")
    field = GF(int(CURVE["p"], 16))
    E = EllipticCurve(field, [0, 7])
    G = E(int(CURVE["gx"], 16), int(CURVE["gy"], 16))
    order = int(CURVE["order"], 16)
    d = secrets.randbelow(order-1) + 1
    Q = d*G
    signatures, nonce_secrets, seen_r = [], [], set()
    for i in range(config["signature_count"]):
        message = f"NTTP/{instance_id}/diagnostic/{i:02d}".encode("ascii")
        h = int.from_bytes(hashlib.sha256(message).digest(), "big")
        while True:
            k = secrets.randbelow(order-1)+1
            r = int((k*G)[0]) % order
            s = pow(k, -1, order) * (h+r*d) % order
            if r and s and r not in seen_r:
                seen_r.add(r)
                break
        signatures.append({"message_hex": message.hex(), "r": hx(r), "s": hx(s),
                           "k_msb": hx(k >> config["nonce_unknown_bits"])})
        nonce_secrets.append(hx(k))
    m3 = {"instance_id": instance_id, "curve": CURVE,
          "public_key": {"x": hx(Q[0]), "y": hx(Q[1])},
          "hash": "SHA-256(message bytes), unsigned big-endian integer",
          "low_s_normalization": False, "nonce_unknown_bits": config["nonce_unknown_bits"],
          "leak_encoding": "k = (int(k_msb,16) << nonce_unknown_bits) + u; 0 <= u < 2^nonce_unknown_bits",
          "signatures": signatures,
          "token_kdf": "SHA256(b'NTTP/ecdsa-key/v1\\x00' || d.to_bytes(32,'big'))",
          "token_box": seal(module3_key(d), tokens["module3"], aad(instance_id, "module3"))}
    master = derive_master_key(manifest, {m: t.hex() for m, t in tokens.items()})
    for name, obj in (("manifest", manifest), ("module1", m1), ("module2", m2), ("module3", m3),
                      ("final.enc", seal(master, flag.encode("utf-8"), aad(instance_id, "final")))):
        dump(challenge / (name + ".json"), obj)
    secret = {"instance_id": instance_id, "flag": flag, "tokens": {m: t.hex() for m, t in tokens.items()},
              "master_key": master.hex(), "module3_aes_key": module3_key(d).hex(),
              "rsa1": {"p": hx(p1), "q": hx(q1), "peer_q": hx(peer_q),
                       "d": hx(pow(e, -1, (p1-1)*(q1-1))),
                       "peer_d": hx(pow(e, -1, (p1-1)*(peer_q-1)))},
              "rsa2": {"p": hx(p2), "q": hx(q2), "d": hx(pow(e, -1, (p2-1)*(q2-1)))},
              "ecdsa": {"d": hx(d), "nonces": nonce_secrets}, "config": config}
    dump(private / "instance.json", secret, private=True)
    (private / "flag.txt").write_text(flag + "\n", encoding="utf-8")
    (private / "flag.txt").chmod(0o600)
    return secret

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT,
                        help="Output root; writes participant/challenge and probset/secrets")
    parser.add_argument("--config", type=Path, default=Path(__file__).with_name("config.json"))
    parser.add_argument("--flag-file", type=Path, help="UTF-8 file; default is a freshly generated flag")
    parser.add_argument("--force", action="store_true", help="Replace an existing instance after verification")
    args = parser.parse_args()
    out = args.output.resolve()
    challenge, private = out / "participant/challenge", out / "probset/secrets"
    if not args.force and ((challenge / "manifest.json").exists() or (private / "instance.json").exists()):
        parser.error("Instance exists; use --force to rotate it.")
    flag = args.flag_file.read_text(encoding="utf-8").strip() if args.flag_file else "COMPFEST18{no_time_to_prime_" + secrets.token_hex(16) + "}"
    if not flag or "\n" in flag or len(flag.encode()) > 512:
        parser.error("Flag must be one nonempty UTF-8 line, at most 512 bytes.")
    if not flag.startswith("COMPFEST18{") or not flag.endswith("}"):
        parser.error("Flag must use COMPFEST18{...} format.")
    sys.path.insert(0, str(ROOT / "probset/tests"))
    from verify import verify_instance
    out.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".nttp-staging-", dir=out) as work:
        stage = Path(work)
        pub, sec = stage / "challenge", stage / "secrets"
        build(pub, sec, flag, read_json(args.config))
        report = verify_instance(pub, sec, scan_root=pub)
        for src, dest in ((pub, challenge), (sec, private)):
            dest.mkdir(parents=True, exist_ok=True)
            for file in src.iterdir():
                os.replace(file, dest / file.name)
        private.chmod(0o700)
        dump(private / "verification.json", report, private=True)
    print("Generated and verified:", report["instance_id"])
    print("Public data:", challenge)
    print("Private author files:", private)
    print("Solver timings:", report["seconds"])

if __name__ == "__main__":
    main()
