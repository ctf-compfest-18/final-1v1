#!/usr/bin/env python3
"""Verify challenge parameters and solutions."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "probset/solver"))
from common import read_json
from solve_all import solve
from app.crypto_core import MODULES, aad, commitment, derive_master_key, unseal, validate_token
from sage.all import is_prime
from sage.version import version as sage_version

ALLOWED_DATA = {"manifest.json", "module1.json", "module2.json", "module3.json", "final.enc.json"}

def require(condition, message):
    if not condition:
        raise AssertionError(message)

def expect_failure(call, message):
    try:
        call()
    except (ValueError, KeyError):
        return
    raise AssertionError(message)

def scan_secrets(root, secret):
    needles = [secret["flag"].encode(), bytes.fromhex(secret["master_key"]), secret["master_key"].encode(),
               bytes.fromhex(secret["module3_aes_key"]), secret["module3_aes_key"].encode()]
    for token in secret["tokens"].values():
        needles.extend([token.encode(), token.upper().encode(), bytes.fromhex(token)])
    values = [*secret["rsa1"].values(), *secret["rsa2"].values(), secret["ecdsa"]["d"], *secret["ecdsa"]["nonces"]]
    for value in values:
        number = int(value, 16)
        needles.extend([value.encode(), value.upper().encode(), str(number).encode(),
                        number.to_bytes((number.bit_length()+7)//8, "big")])
    count = 0
    for path in Path(root).rglob("*"):
        if path.is_symlink():
            raise AssertionError(f"Symlink forbidden in participant package: {path}")
        if not path.is_file():
            continue
        # Local Python caches are never packaged; all source/data files are scanned.
        if any(part in {"__pycache__", ".venv", ".git"} for part in path.parts):
            continue
        require(path.suffix not in (".zip", ".pem", ".key"), f"Unexpected sensitive/archive file: {path}")
        data = path.read_bytes()
        for needle in needles:
            require(needle not in data, f"Secret leak in {path.name}")
        count += 1
    return count

def verify_instance(challenge, private, scan_root=None):
    challenge, private = Path(challenge), Path(private)
    require({p.name for p in challenge.iterdir()} == ALLOWED_DATA, "Unexpected public data files")
    manifest = read_json(challenge / "manifest.json")
    secret = read_json(private / "instance.json")
    require(manifest["instance_id"] == secret["instance_id"], "Instance mismatch")
    require((private / "flag.txt").read_text().strip() == secret["flag"], "Flag file mismatch")
    m1, m2, m3 = [read_json(challenge / f"module{i}.json") for i in (1,2,3)]
    for obj in (m1, m2, m3):
        require(obj["instance_id"] == manifest["instance_id"], "Mixed public instances")
    n1, peer, n2 = int(m1["n"], 16), int(m1["peer_n"], 16), int(m2["n"], 16)
    p1, q1, pq = [int(secret["rsa1"][k], 16) for k in ("p", "q", "peer_q")]
    p2, q2 = [int(secret["rsa2"][k], 16) for k in ("p", "q")]
    require(n1 == p1*q1 and peer == p1*pq and n2 == p2*q2, "RSA modulus mismatch")
    require(len({p1, q1, pq, p2, q2}) == 5, "Unexpected prime reuse")
    require(all(is_prime(p) and p.bit_length() == 512 for p in (p1,q1,pq,p2,q2)), "Bad primes")
    require(all(n.bit_length() == 1024 for n in (n1,peer,n2)), "Bad modulus sizes")
    require(math.gcd(n1, peer) == p1 and math.gcd(n1,n2) == math.gcd(peer,n2) == 1, "Unintended GCD shortcut")
    require(abs(p1-q1).bit_length() >= 496 and abs(p2-q2).bit_length() >= 496, "Close primes")
    require(p2 >> m2["unknown_bits"] == int(m2["p_msb"],16), "Prime leak mismatch")
    require(len(m3["signatures"]) == 8, "Expected 8 signatures")
    require(len(set(secret["ecdsa"]["nonces"])) == 8, "Repeated nonce")
    require(len({s["r"] for s in m3["signatures"]}) == 8, "Repeated r shortcut")
    require(not m3["low_s_normalization"], "Nonce relation requires raw s")
    for sig, nonce in zip(m3["signatures"], secret["ecdsa"]["nonces"]):
        require(int(nonce,16) >> 128 == int(sig["k_msb"],16), "Wrong nonce MSB")
    result = solve(challenge, verbose=False)
    require(result["tokens"] == secret["tokens"], "Recovered tokens differ")
    require(result["flag"] == secret["flag"], "Recovered flag differs")
    require(result["master_key"] == secret["master_key"], "Recovered master key differs")
    for m in MODULES:
        require(not validate_token(manifest,m,"00"*32), "Zero token accepted")
        require(not validate_token(manifest,m,"xyz"), "Malformed token accepted")
        missing = dict(result["tokens"]); missing.pop(m)
        expect_failure(lambda: derive_master_key(manifest,missing), "Missing token accepted")
        wrong = dict(result["tokens"]); wrong[m] = "00"*32
        expect_failure(lambda: derive_master_key(manifest,wrong), "Incorrect token accepted")
    swapped = dict(result["tokens"])
    swapped["module1"], swapped["module2"] = swapped["module2"], swapped["module1"]
    expect_failure(lambda: derive_master_key(manifest,swapped), "Swapped token accepted")
    key = bytes.fromhex(result["master_key"])
    box = read_json(challenge / "final.enc.json")
    tampered = dict(box)
    tag = bytearray.fromhex(box["tag"]); tag[0] ^= 1; tampered["tag"] = tag.hex()
    expect_failure(lambda: unseal(key,tampered,aad(manifest["instance_id"],"final")), "Tampered tag accepted")
    expect_failure(lambda: unseal(key,box,aad("different-instance","final")), "Wrong AAD accepted")
    # Even patching local commitments/status cannot make a wrong master key decrypt.
    forged = dict(manifest)
    forged["commitments"] = {m: commitment(manifest["instance_id"], m, bytes(32)) for m in MODULES}
    fake_key = derive_master_key(forged, {m: "00"*32 for m in MODULES})
    expect_failure(lambda: unseal(fake_key,box,aad(manifest["instance_id"],"final")), "GUI bypass decrypted vault")
    files = scan_secrets(scan_root or challenge, secret)
    return {"status": "PASS", "instance_id": manifest["instance_id"], "sage": sage_version,
            "seconds": result["seconds"], "files_scanned": files,
            "checks": ["RSA structure/independence", "ECDSA signatures and leaks", "three public-only solvers",
                       "master key and final flag", "wrong/missing/swapped tokens", "GCM tampering and patched-client rejection", "plaintext secret scan"],
            "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(challenge.glob("*.json"))}}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = verify_instance(args.root / "participant/challenge", args.root / "probset/secrets",
                             args.root / "participant")
    output = json.dumps(report, indent=2)
    if args.report:
        args.report.write_text(output + "\n")
    print(output)

if __name__ == "__main__":
    main()
