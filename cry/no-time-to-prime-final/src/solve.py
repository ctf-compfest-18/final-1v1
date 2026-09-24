#!/usr/bin/env python3
import ast
import hashlib
import math
import re
from pathlib import Path

N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141


def inv(a, m):
    return pow(a % m, -1, m)


def egcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def exp_signed(c, e, n):
    if e >= 0:
        return pow(c, e, n)
    return pow(inv(c, n), -e, n)


def parse(path):
    vals = {}
    section = None
    for raw in Path(path).read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('[') and line.endswith(']'):
            section = line[1:-1]
            continue
        if '=' not in line:
            continue
        k, v = [x.strip() for x in line.split('=', 1)]
        vals[(section, k)] = v
    return vals


def stream_xor(data, d):
    seed = d.to_bytes(32, 'big')
    ks = hashlib.shake_256(b'no-time-to-prime/final|' + seed).digest(len(data))
    return bytes(a ^ b for a, b in zip(data, ks))


def solve(output_path):
    v = parse(output_path)

    # Stage 1 -- shared RSA prime.
    e = int(v['stage1', 'e'])
    n1 = int(v['stage1', 'n1'])
    n2 = int(v['stage1', 'n2'])
    c1 = int(v['stage1', 'c1'])
    p = math.gcd(n1, n2)
    assert 1 < p < n1
    q1 = n1 // p
    phi = (p - 1) * (q1 - 1)
    d1 = inv(e, phi)
    m1 = pow(c1, d1, n1)
    token1 = m1.to_bytes((m1.bit_length() + 7) // 8, 'big')
    assert token1.startswith(b'NTTP1:')
    print('[+] stage1:', token1.decode())

    # Stage 2 -- unmask c_b using stage1 token, then common-modulus attack.
    n = int(v['stage2', 'n'])
    ea = int(v['stage2', 'e_a'])
    eb = int(v['stage2', 'e_b'])
    ca = int(v['stage2', 'c_a'])
    cb_masked = int(v['stage2', 'c_b_masked'])
    kbytes = (n.bit_length() + 7) // 8
    mask = hashlib.shake_256(b'no-time-to-prime/stage2|' + token1).digest(kbytes)
    cb = cb_masked ^ int.from_bytes(mask, 'big')

    g, x, y = egcd(ea, eb)
    assert g == 1
    m2 = (exp_signed(ca, x, n) * exp_signed(cb, y, n)) % n
    bridge = m2.to_bytes((m2.bit_length() + 7) // 8, 'big')
    assert bridge.startswith(b'NTTP2:')
    relation_b = int(bridge.split(b':', 1)[1])
    print('[+] stage2:', bridge.decode())

    # Stage 3 -- solve affine-related ECDSA nonces.
    a = int(v['stage3', 'a'])
    z1 = int(v['stage3', 'z1'])
    r1 = int(v['stage3', 'r1'])
    s1 = int(v['stage3', 's1'])
    z2 = int(v['stage3', 'z2'])
    r2 = int(v['stage3', 'r2'])
    s2 = int(v['stage3', 's2'])

    t = (r2 * inv(r1, N)) % N
    coef = (s2 * a - t * s1) % N
    rhs = (z2 - t * z1 - s2 * relation_b) % N
    k1 = (rhs * inv(coef, N)) % N
    d = ((s1 * k1 - z1) * inv(r1, N)) % N
    print('[+] stage3 private key:', hex(d))

    flag_ct = bytes.fromhex(v['final', 'flag_ct'])
    flag = stream_xor(flag_ct, d)
    print('[+] flag:', flag.decode())
    return flag


if __name__ == '__main__':
    here = Path(__file__).resolve().parent
    solve(here / 'output.txt')
