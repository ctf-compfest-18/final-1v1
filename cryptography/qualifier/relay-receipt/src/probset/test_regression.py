"""Test fresh instances and leading-zero tokens."""
from unittest.mock import patch
import generate
from solve import recover


def main():
    flag = b'COMPFEST18{regression_only}'
    for _ in range(3):
        transcript, private = generate.generate(flag)
        got, state = recover(transcript)
        assert got == flag and state['d'] == private['d']
    # Scoped only to generator's two byte secrets; scalar/prime/IV RNG stays fresh.
    ticket = b'\x00' * 31 + b'\x01'
    token = b'\x00' * 31 + b'\x02'
    with patch.object(generate.secrets, 'token_bytes', side_effect=[ticket, token]):
        transcript, private = generate.generate(flag)
    got, state = recover(transcript)
    assert got == flag and state['ticket'] == ticket.hex() and state['token'] == token.hex()
    print('PASS: three fresh instances and 31 leading-zero-byte ticket/token.')

if __name__ == '__main__':
    main()
