"""RSA decryption helpers."""
import sys
from pathlib import Path
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "participant"))
from app.crypto_core import read_json, validate_token

DEFAULT_CHALLENGE = ROOT / "participant" / "challenge"

def rsa_token(obj, p):
    n, e = int(obj["n"], 16), obj["e"]
    p = int(p)
    if not 1 < p < n or n % p:
        raise ValueError("Not a nontrivial factor")
    q = n // p
    d = pow(e, -1, (p - 1) * (q - 1))
    key = RSA.construct((n, e, d, p, q))
    token = PKCS1_OAEP.new(key, hashAlgo=SHA256,
                         label=obj["oaep_label"].encode("ascii")).decrypt(bytes.fromhex(obj["ciphertext"]))
    if len(token) != 32:
        raise ValueError("Unexpected plaintext length")
    return token.hex()

def checked(challenge, module, token):
    manifest = read_json(Path(challenge) / "manifest.json")
    if not validate_token(manifest, module, token):
        raise ValueError("Recovered token failed commitment")
    return token
