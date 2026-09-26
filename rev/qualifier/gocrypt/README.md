# gocrypt

author: kannrisha

## Description

I encrypted my flag and forgot how to get it back. At least I still have the encryptor.

## Difficulty

easy

## Additional Hints

1. The encryptor uses AES-CTR. Reusing the nonce would also reuse its keystream. Can you make the encryptor use the nonce from `flag.enc`?
2. **Desperate hint — release 5 minutes before time is over:** `flag.enc` is `GOCRYPT1` (8 bytes), the 16-byte nonce, then ciphertext. Encrypt a file of null bytes with `chall`, patching or instrumenting it to use that same nonce. Its ciphertext is the keystream; XOR it with the ciphertext from `flag.enc` to recover the plaintext.

## Flag

`COMPFEST18{8f335c2baa8af8c70538950f}`

## Archive Password

`24bc722f6170529c69ba844c`
