"""Verify the transcript and recovered flag."""
import hashlib
import json
import math
import shutil
import subprocess
import sys
import tempfile
import time
from copy import deepcopy
from pathlib import Path
from Crypto.Hash import SHA256
from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Util.number import isPrime
from generate import load_construction
from solve import recover

ROOT = Path(__file__).resolve().parents[1]

def main():
    start = time.perf_counter()
    public = json.loads((ROOT/'participant/output.json').read_text())
    private = json.loads((ROOT/'probset/secrets.json').read_text())
    flag = (ROOT/'probset/flag.txt').read_bytes().rstrip(b'\r\n')
    c = load_construction()
    p, q, t, u, v = [private[x] for x in ('p', 'q', 't', 'u', 'v')]
    primes = [p, q, t, u, v]
    assert len(set(primes)) == 5
    assert all(x.bit_length() == 1024 and isPrime(x) for x in primes)
    assert all(math.gcd(e, x-1) == 1 for x in primes for e in (65537, 65539))
    n0, n1 = [row['n'] for row in public['directory']]
    assert (n0, n1) == (p*q, p*t)
    assert math.gcd(n0, n1) == p
    assert math.gcd(n0*n1, u*v) == 1
    assert private['k2'] == (private['a']*private['k']+private['b']) % c.ORDER
    assert 0 < private['k2'] < c.ORDER and private['k2'] != private['k']
    recovered_flag, state = recover(public)
    assert recovered_flag == flag
    assert all(state[x] == private[x] for x in state)
    Q = ECC.construct(curve='P-256', d=private['d']).pointQ
    assert (int(Q.x), int(Q.y)) == (public['public_key']['x'], public['public_key']['y'])
    verifier = DSS.new(ECC.construct(curve='P-256', point_x=int(Q.x), point_y=int(Q.y)), 'fips-186-3')
    for sig, k in zip(public['receipts'], (private['k'], private['k2'])):
        assert sig == c.sign(private['d'], k, bytes.fromhex(sig['message']))
        verifier.verify(SHA256.new(bytes.fromhex(sig['message'])),
                        sig['r'].to_bytes(32, 'big')+sig['s'].to_bytes(32, 'big'))
    assert public['receipts'][0]['r'] != public['receipts'][1]['r']
    # Exact construction parity, excluding fresh AES IV/ciphertexts.
    from solve import unseal
    ticket, token = bytes.fromhex(private['ticket']), bytes.fromhex(private['token'])
    delivery = json.loads(unseal('delivery', ticket, public['delivery']))
    assert delivery == dict(n=u*v, e=[65537, 65539], c=[pow(int.from_bytes(token,'big'),e,u*v) for e in (65537,65539)])
    assert json.loads(unseal('policy', token, public['policy'])) == dict(a=private['a'], b=private['b'])
    for label in ('delivery', 'policy', 'vault'):
        damaged = deepcopy(public)
        tag = bytearray.fromhex(damaged[label]['tag'])
        tag[0] ^= 1
        damaged[label]['tag'] = tag.hex()
        try:
            recover(damaged)
        except ValueError:
            pass
        else:
            raise AssertionError('Corrupted '+label+' was accepted')
    files = sorted(x.name for x in (ROOT/'participant').iterdir() if x.is_file())
    assert files == ['README.md', 'chall.py', 'output.json']
    for path in (ROOT/'participant').iterdir():
        if not path.is_file():
            continue
        blob = path.read_bytes()
        assert flag not in blob
        for name, value in private.items():
            if name == 'rsa_private_exponents':
                values = value
            else:
                values = [value]
            for secret in values:
                assert str(secret).encode() not in blob, (path.name, name)
    # Run the solver with only the distributed files.
    with tempfile.TemporaryDirectory(prefix='relay-public-only-') as tmp:
        tmp = Path(tmp)
        shutil.copytree(ROOT/'participant', tmp/'participant', ignore=shutil.ignore_patterns('__pycache__'))
        shutil.copyfile(ROOT/'probset/solve.py', tmp/'solve.py')
        runs = [subprocess.check_output([sys.executable, '-I', str(tmp/'solve.py'), str(tmp/'participant')], cwd=tmp) for _ in range(2)]
        assert runs[0] == runs[1] == flag+b'\n'
        emitted = subprocess.check_output([sys.executable, '-I', str(tmp/'participant/chall.py')], cwd=tmp)
        assert json.loads(emitted) == public
    print(f'PASS: parameters, independent ECDSA verification, chain, tamper rejection, leak scan, isolated deterministic solve ({time.perf_counter()-start:.2f}s).')

if __name__ == '__main__':
    main()
