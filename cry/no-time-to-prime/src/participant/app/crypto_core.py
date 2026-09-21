"""Token validation and vault decryption."""
import hashlib
import hmac
import json
import re
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import HKDF

MODULES = ("module1", "module2", "module3")
TOKEN_RE = re.compile(r"[0-9a-fA-F]{64}\Z")

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def token_bytes(value):
    if not isinstance(value, str) or not TOKEN_RE.fullmatch(value.strip()):
        raise ValueError("Token harus tepat 64 digit hex (32 byte).")
    return bytes.fromhex(value.strip())

def commitment(instance_id, module, token):
    if module not in MODULES or len(token) != 32:
        raise ValueError("Invalid module/token length")
    return hashlib.sha256(b"NTTP/commit/v1\0" + instance_id.encode("ascii")
                          + b"\0" + module.encode("ascii") + b"\0" + token).hexdigest()

def validate_token(manifest, module, value):
    if module not in MODULES:
        return False
    try:
        actual = commitment(manifest["instance_id"], module, token_bytes(value))
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, manifest["commitments"][module])

def derive_master_key(manifest, tokens):
    if set(tokens) != set(MODULES):
        raise ValueError("Diperlukan ketiga token, sesuai urutan modul.")
    if not all(validate_token(manifest, m, tokens[m]) for m in MODULES):
        raise ValueError("Token tidak cocok dengan instance ini.")
    ikm = b"".join(token_bytes(tokens[m]) for m in MODULES)
    return HKDF(ikm, 32, bytes.fromhex(manifest["kdf"]["salt"]), SHA256,
                context=("NTTP/final/v1/" + manifest["instance_id"]).encode("ascii"))

def aad(instance_id, label):
    return ("NTTP/" + instance_id + "/" + label).encode("ascii")

def seal(key, plaintext, associated_data):
    cipher = AES.new(key, AES.MODE_GCM, mac_len=16)
    cipher.update(associated_data)
    ciphertext, tag = cipher.encrypt_and_digest(plaintext)
    return {"algorithm": "AES-256-GCM", "nonce": cipher.nonce.hex(),
            "ciphertext": ciphertext.hex(), "tag": tag.hex()}

def unseal(key, envelope, associated_data):
    if envelope["algorithm"] != "AES-256-GCM":
        raise ValueError("Unsupported cipher")
    cipher = AES.new(key, AES.MODE_GCM, nonce=bytes.fromhex(envelope["nonce"]), mac_len=16)
    cipher.update(associated_data)
    return cipher.decrypt_and_verify(bytes.fromhex(envelope["ciphertext"]),
                                     bytes.fromhex(envelope["tag"]))

def module3_key(private_scalar):
    return hashlib.sha256(b"NTTP/ecdsa-key/v1\0" + int(private_scalar).to_bytes(32, "big")).digest()

def recover_final(challenge_dir, tokens):
    challenge_dir = Path(challenge_dir)
    manifest = read_json(challenge_dir / "manifest.json")
    key = derive_master_key(manifest, tokens)
    flag = unseal(key, read_json(challenge_dir / "final.enc.json"),
                  aad(manifest["instance_id"], "final"))
    return key, flag.decode("utf-8")
