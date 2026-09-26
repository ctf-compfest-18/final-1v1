BLOCK_SIZE = 5
MOD = 1 << (8 * BLOCK_SIZE)

header = bytes.fromhex("89504e470d0a1a0a0000000d49484452")

with open("flag.enc", "rb") as f:
    encrypted = f.read()

if len(encrypted) < len(header):
    raise ValueError("Expected at least 16 encrypted bytes.")

known_keystream = bytes(
    x ^ y for x, y in zip(encrypted[:len(header)], header)
)

# The first 15 known bytes reveal three complete 40-bit states.
s0, s1, s2 = [
    int.from_bytes(known_keystream[i:i + BLOCK_SIZE], "big")
    for i in range(0, 3 * BLOCK_SIZE, BLOCK_SIZE)
]

d0 = (s1 - s0) % MOD
d1 = (s2 - s1) % MOD

a = (d1 * pow(d0, -1, MOD)) % MOD
b = (s1 - a * s0) % MOD

# The remaining known byte verifies the first byte of state s3.
s3 = (a * s2 + b) % MOD
if s3.to_bytes(BLOCK_SIZE, "big")[0] != known_keystream[15]:
    raise ValueError("Recovered parameters fail the header check.")

state = s0
image = bytearray()

for offset in range(0, len(encrypted), BLOCK_SIZE):
    block = encrypted[offset:offset + BLOCK_SIZE]
    keystream = state.to_bytes(BLOCK_SIZE, "big")

    image.extend(x ^ y for x, y in zip(block, keystream))
    state = (a * state + b) % MOD

with open("recovered.png", "wb") as f:
    f.write(image)

print("Saved recovered.png")