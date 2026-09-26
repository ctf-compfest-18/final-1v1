# my

author: xymbol

## Description

my bini

## Flag

`COMPFEST18{Lima_ribu_???_miskin_sulit_susah_ripuh_busung_lapar}`

## Archive Password

`0258578ff204c91650891d75`

## Hints

2. They use the same key to encrypt. Reproduce the shuffle on the known image first
3. This is a known-plaintext attack against a Hill cipher with CBC-like chaining. Remove the previous ciphertext block first, then recover the key matrix mod 256.
4. The inverse of `(x, y) -> (x + 67y, 76x + 5093y)` mod 256 is `(x, y) -> (229x + 189y, 180x + y)`. After recovering key just decrypt then unshuffle and voila!