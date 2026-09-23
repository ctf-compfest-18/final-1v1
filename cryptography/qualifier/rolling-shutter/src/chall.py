import os

BLOCK_SIZE = 5
MOD = 1 << (8 * BLOCK_SIZE)

state = int.from_bytes(os.urandom(BLOCK_SIZE), "big")
a = int.from_bytes(os.urandom(BLOCK_SIZE), "big") | 1
b = int.from_bytes(os.urandom(BLOCK_SIZE), "big") | 1

with open("flag.png", "rb") as f:
    image = f.read()

encrypted = bytearray()

for offset in range(0, len(image), BLOCK_SIZE):
    block = image[offset:offset + BLOCK_SIZE]
    keystream = state.to_bytes(BLOCK_SIZE, "big")

    encrypted.extend(x ^ y for x, y in zip(block, keystream))
    state = (a * state + b) % MOD

with open("flag.enc", "wb") as f:
    f.write(encrypted)

print("Saved flag.enc")