# Write Up Rolling Shutter

## Encryption

Let M = 2^32. Generate a random 32-bit starting state s0, a random odd multiplier a, and a random odd increment b. The `| 1` expressions force the least significant bit to one, making the parameters odd.

For each block of at most four image bytes:

1. Serialize the current state as four big-endian bytes.
2. XOR the image bytes with the corresponding state bytes.
3. Append the result to the ciphertext.
4. Update the state: s_(i+1) = (a*s_i + b) mod M.

The first block uses s0 before any update. The final partial block uses only the required bytes; padding is unnecessary.

## Recover the states from the PNG header

A standard PNG starts with:

```text
89 50 4e 47 0d 0a 1a 0a 00 00 00 0d 49 48 44 52
```

These are the eight-byte signature, four-byte IHDR data length (13), and four-byte ASCII chunk type IHDR. They are independent of image dimensions and pixel contents.

XOR these bytes with the first 16 ciphertext bytes. Split the result into four groups of four bytes and interpret each as a big-endian integer. This gives s0, s1, s2, and s3.

## Recover the hidden parameters

The recurrence gives:

```text
s1 = a*s0 + b  (mod M)
s2 = a*s1 + b  (mod M)
```

Subtract the first equation from the second:

```text
s2 - s1 = a*(s1 - s0)  (mod M)
```

Define d0 = (s1 - s0) mod M and d1 = (s2 - s1) mod M. Then:

```text
a = d1 * inverse(d0, M) mod M
b = (s1 - a*s0) mod M
```

Python computes the modular inverse with `pow(d0, -1, M)`. Ordinary integer or floating-point division is not a substitute.

### Why the inverse always exists

Since a and b are odd:

```text
s1 - s0 = (a - 1)*s0 + b  (mod 2^32)
```

The first term is even and b is odd, so the difference is odd. Every odd number is coprime to 2^32 and therefore invertible modulo 2^32. This prevents randomly unsolvable instances of the intended recovery step.

Use the fourth state to check `(a*s2 + b) % M == s3`. Only the first three states are needed to recover the parameters; the fourth provides a consistency check.

## Decrypt the image

Reset the state to s0. Reproduce each four-byte keystream block, XOR it with the ciphertext, and update using the recovered a and b. XOR cancels itself, so the original image is recovered exactly. Save as `recovered.png` and open it to read the flag.

The generator state is emitted directly as the keystream. A known file header exposes that state, and the linear recurrence lets the attacker recover the hidden parameters and predict future states. This is an intentionally insecure custom cipher.