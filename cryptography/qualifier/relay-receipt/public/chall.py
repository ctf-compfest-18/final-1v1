"""Receipt construction and public transcript."""
import hashlib
import json
from pathlib import Path
from Crypto.Cipher import AES
from Crypto.PublicKey import ECC

ORDER = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
G = ECC.construct(curve="P-256", d=1).pointQ
MESSAGES = [b"COMPFEST/relay/receipt/0", b"COMPFEST/relay/receipt/1"]

def key(label, raw):
    return hashlib.sha256(b"relay/" + label.encode() + b"\x00" + raw).digest()

def seal(label, raw, plaintext):
    cipher = AES.new(key(label, raw), AES.MODE_GCM)
    cipher.update(label.encode())
    ct, tag = cipher.encrypt_and_digest(plaintext)
    return dict(iv=cipher.nonce.hex(), ct=ct.hex(), tag=tag.hex())

def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()

def sign(d, nonce, message):
    z = int.from_bytes(hashlib.sha256(message).digest(), "big")
    r = int((nonce * G).x) % ORDER
    s = pow(nonce, -1, ORDER) * (z + r * d) % ORDER
    return dict(message=message.hex(), r=r, s=s)

def build(directory_keys, delivery_key, ticket, token, d, k, a, b, flag):
    directory = [dict(n=left * right, e=65537) for left, right in directory_keys]
    n = delivery_key[0] * delivery_key[1]
    m = int.from_bytes(token, "big")
    delivery = dict(n=n, e=[65537, 65539], c=[pow(m, e, n) for e in (65537, 65539)])
    policy = dict(a=a, b=b)
    nonces = [k, (a * k + b) % ORDER]
    Q = d * G
    return dict(
        version=1,
        directory=directory,
        ticket=pow(int.from_bytes(ticket, "big"), 65537, directory[0]["n"]),
        delivery=seal("delivery", ticket, encode(delivery)),
        policy=seal("policy", token, encode(policy)),
        receipts=[sign(d, nonce, msg) for nonce, msg in zip(nonces, MESSAGES)],
        public_key=dict(x=int(Q.x), y=int(Q.y)),
        vault=seal("vault", d.to_bytes(32, "big"), flag),
    )

if __name__ == "__main__":
    print(json.dumps(json.loads(Path(__file__).with_name("output.json").read_text()), indent=2))
