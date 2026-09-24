# NOT shipped to participants.
from Crypto.Util.number import getPrime, isPrime
from random import randrange

FLAG = b"COMPFEST18{f3rm4t_kn3w_cl0s3_pr1m3s_4r3_w34k}"

# The published instance reuses the exact primes of the original "Close Primes"
# release, so every number in the Fermat half of the writeup stays valid and the
# modulus is byte-identical to the soal that was already reviewed.
_P = 6703903964971298549787012499102924481204972448254168472572572803398595616708693312243200493876332803758231553138066346839008210339789110853482192169117709
_Q = 6703903964971298549787012499102924481204972448254168472572572803398595616708693312243200493876332803758231553138066346839008210339789110853482193182786281


def generate_primes(nbit, fresh=False):
    """The intern's 'shortcut': q is picked right next to p (|p - q| ~ 2^30)."""
    if not fresh:
        assert _P.bit_length() == _Q.bit_length() == nbit
        return _P, _Q

    while True:
        p = getPrime(nbit)
        q = p + randrange(1 << 29, 1 << 30)
        q += 1 - (q & 1)
        while not isPrime(q):
            q += 2
        if q.bit_length() == nbit:
            return p, q
