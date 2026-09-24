#!/usr/bin/env python3
import hashlib
import math
import secrets
from pathlib import Path

# secp256k1
P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
A = 0
B = 7
GX = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GY = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8
N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
G = (GX, GY)


def inv(a, m):
    return pow(a % m, -1, m)


def is_probable_prime(n, rounds=24):
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False

    d = n - 1
    s = 0
    while d % 2 == 0:
        s += 1
        d //= 2

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def get_prime(bits):
    while True:
        x = secrets.randbits(bits)
        x |= (1 << (bits - 1)) | 1
        if is_probable_prime(x):
            return x


def point_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P == 0:
        return None
    if p1 == p2:
        lam = ((3 * x1 * x1 + A) * inv(2 * y1, P)) % P
    else:
        lam = ((y2 - y1) * inv(x2 - x1, P)) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return x3, y3


def scalar_mult(k, point=G):
    result = None
    addend = point
    while k:
        if k & 1:
            result = point_add(result, addend)
        addend = point_add(addend, addend)
        k >>= 1
    return result


def ecdsa_sign(d, k, msg):
    z = int.from_bytes(hashlib.sha256(msg).digest(), 'big') % N
    r = scalar_mult(k)[0] % N
    if r == 0:
        raise ValueError('bad r')
    s = (inv(k, N) * (z + r * d)) % N
    if s == 0:
        raise ValueError('bad s')
    return z, r, s


def stream_xor(data, secret_int):
    seed = secret_int.to_bytes(32, 'big')
    ks = hashlib.shake_256(b'no-time-to-prime/final|' + seed).digest(len(data))
    return bytes(a ^ b for a, b in zip(data, ks))


def emit(output_path: Path, flag: bytes):
    # Stage 1
    e = 65537
    while True:
        p = get_prime(384)
        q1 = get_prime(384)
        q2 = get_prime(384)
        if q1 == q2:
            continue
        if math.gcd(e, (p - 1) * (q1 - 1)) == 1:
            break

    n1 = p * q1
    n2 = p * q2
    token1 = b'NTTP1:' + secrets.token_hex(12).encode()
    m1 = int.from_bytes(token1, 'big')
    c1 = pow(m1, e, n1)

    # Stage 2
    ea, eb = 65537, 17
    while True:
        p2 = get_prime(384)
        q2b = get_prime(384)
        phi2 = (p2 - 1) * (q2b - 1)
        if math.gcd(ea * eb, phi2) == 1:
            break
    n3 = p2 * q2b

    relation_b = secrets.randbelow(1 << 120) + (1 << 119)
    bridge2 = b'NTTP2:' + str(relation_b).encode()
    m2 = int.from_bytes(bridge2, 'big')
    if m2 >= n3 or math.gcd(m2, n3) != 1:
        raise RuntimeError('regenerate: stage2 message invalid')

    ca = pow(m2, ea, n3)
    cb = pow(m2, eb, n3)
    kbytes = (n3.bit_length() + 7) // 8
    mask = hashlib.shake_256(b'no-time-to-prime/stage2|' + token1).digest(kbytes)
    cb_masked = cb ^ int.from_bytes(mask, 'big')

    # Stage 3
    a = 7
    d = secrets.randbelow(N - 1) + 1
    pub = scalar_mult(d)
    while True:
        k1 = secrets.randbelow(N - 1) + 1
        k2 = (a * k1 + relation_b) % N
        if k2 == 0:
            continue
        try:
            msg1 = b'nttp signature 01'
            msg2 = b'nttp signature 02'
            z1, r1, s1 = ecdsa_sign(d, k1, msg1)
            z2, r2, s2 = ecdsa_sign(d, k2, msg2)
            t = (r2 * inv(r1, N)) % N
            coef = (s2 * a - t * s1) % N
            if coef != 0:
                break
        except ValueError:
            pass

    flag_ct = stream_xor(flag, d)

    text = f'''# No Time to Prime -- captured output\n\n[stage1]\ne = {e}\nn1 = {n1}\nn2 = {n2}\nc1 = {c1}\n\n[stage2]\nn = {n3}\ne_a = {ea}\ne_b = {eb}\nc_a = {ca}\nc_b_masked = {cb_masked}\n\n[stage3]\ncurve = secp256k1\na = {a}\nmsg1 = {msg1!r}\nz1 = {z1}\nr1 = {r1}\ns1 = {s1}\nmsg2 = {msg2!r}\nz2 = {z2}\nr2 = {r2}\ns2 = {s2}\npub_x = {pub[0]}\npub_y = {pub[1]}\n\n[final]\nflag_ct = {flag_ct.hex()}\n'''
    output_path.write_text(text)


if __name__ == '__main__':
    here = Path(__file__).resolve().parent
    flag = (here / 'flag.txt').read_bytes().strip()
    emit(here / 'output.txt', flag)
    print('generated:', here / 'output.txt')
