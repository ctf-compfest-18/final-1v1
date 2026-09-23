"""Generate a receipt transcript."""
import argparse
import importlib.util
import json
import math
import secrets
from pathlib import Path
from Crypto.Util.number import getPrime

ROOT = Path(__file__).resolve().parents[1]

def load_construction():
    spec = importlib.util.spec_from_file_location("relay_construction", ROOT / "participant/chall.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def generate(flag):
    c = load_construction()
    primes = []
    while len(primes) < 5:
        prime = getPrime(1024)
        if prime not in primes and all(math.gcd(e, prime-1) == 1 for e in (65537, 65539)):
            primes.append(prime)
    p, q, t, u, v = primes
    ticket, token = secrets.token_bytes(32), secrets.token_bytes(32)
    while not int.from_bytes(ticket, "big"):
        ticket = secrets.token_bytes(32)
    while not int.from_bytes(token, "big"):
        token = secrets.token_bytes(32)
    d = secrets.randbelow(c.ORDER-1)+1
    while True:
        k = secrets.randbelow(c.ORDER-1)+1
        a = secrets.randbelow(c.ORDER-2)+2
        b = secrets.randbelow(c.ORDER-1)+1
        k2 = (a*k+b) % c.ORDER
        if k2 in (0, k):
            continue
        sig1, sig2 = [c.sign(d, nonce, msg) for nonce, msg in zip((k, k2), c.MESSAGES)]
        if not all(s[field] for s in (sig1, sig2) for field in ("r", "s")):
            continue
        if sig1["r"] == sig2["r"]:
            continue
        if (a*sig2["s"]*sig1["r"] - sig1["s"]*sig2["r"]) % c.ORDER:
            break
    public = c.build(((p, q), (p, t)), (u, v), ticket, token, d, k, a, b, flag)
    private = dict(p=p, q=q, t=t, u=u, v=v, ticket=ticket.hex(), token=token.hex(),
                   d=d, k=k, k2=k2, a=a, b=b)
    private["rsa_private_exponents"] = [pow(65537, -1, (p-1)*(q-1)),
        pow(65537, -1, (p-1)*(t-1)), pow(65537, -1, (u-1)*(v-1)),
        pow(65539, -1, (u-1)*(v-1))]
    return public, private

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--flag-file", type=Path, default=ROOT/"probset/flag.txt")
    args = parser.parse_args()
    flag = args.flag_file.read_bytes().rstrip(b"\r\n")
    if not flag.startswith(b"COMPFEST18{") or not flag.endswith(b"}"):
        raise ValueError("Flag must use COMPFEST18{...} format")
    public, private = generate(flag)
    # Verify in memory before replacing instance files.
    from solve import recover
    assert recover(public)[0] == flag
    (ROOT/"participant/output.json").write_text(json.dumps(public, indent=2)+"\n")
    (ROOT/"probset/secrets.json").write_text(json.dumps(private, indent=2)+"\n")
    (ROOT/"probset/flag.txt").write_bytes(flag+b"\n")
    print("Generated and solved a fresh instance. Distribute participant/ only.")

if __name__ == "__main__":
    main()
