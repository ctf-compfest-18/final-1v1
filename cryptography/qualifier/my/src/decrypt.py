from PIL import Image
from math import gcd

MOD = 256
IV = [73, 201]
ROUNDS = 7

CALIB_PLAIN = "my.png"
CALIB_ENC = "my.enc.png"
TARGET_ENC = "flag.enc.png"
OUTPUT = "recovered.png"


def shuffle(img):
    shuffled = img.copy()

    for _ in range(ROUNDS):
        next_img = Image.new("L", img.size)
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                x_new = (x + 67 * y) % img.size[0]
                y_new = (76 * x + 5093 * y) % img.size[1]
                next_img.putpixel((x_new, y_new), shuffled.getpixel((x, y)))
        shuffled = next_img

    return shuffled


def unshuffle(img):
    unshuffled = img.copy()

    for _ in range(ROUNDS):
        previous_img = Image.new("L", img.size)
        for x in range(img.size[0]):
            for y in range(img.size[1]):
                x_old = (229 * x + 189 * y) % img.size[0]
                y_old = (180 * x + y) % img.size[1]
                previous_img.putpixel((x_old, y_old), unshuffled.getpixel((x, y)))
        unshuffled = previous_img

    return unshuffled

def matrix_inv_2x2(M):
    a, b = M[0]
    c, d = M[1]

    det = (a * d - b * c) % MOD

    if gcd(det, MOD) != 1:
        raise ValueError("Matrix is not invertible modulo 256")

    det_inv = pow(det, -1, MOD)

    return [
        [
            (det_inv * d) % MOD,
            (det_inv * -b) % MOD
        ],
        [
            (det_inv * -c) % MOD,
            (det_inv * a) % MOD
        ]
    ]


def matrix_mul_2x2(A, B):
    return [
        [
            (A[0][0] * B[0][0] + A[0][1] * B[1][0]) % MOD,
            (A[0][0] * B[0][1] + A[0][1] * B[1][1]) % MOD
        ],
        [
            (A[1][0] * B[0][0] + A[1][1] * B[1][0]) % MOD,
            (A[1][0] * B[0][1] + A[1][1] * B[1][1]) % MOD
        ]
    ]


def matrix_vec_mul(M, v):
    return [
        (M[0][0] * v[0] + M[0][1] * v[1]) % MOD,
        (M[1][0] * v[0] + M[1][1] * v[1]) % MOD
    ]



plain_img = Image.open(CALIB_PLAIN).convert("L")
enc_img = Image.open(CALIB_ENC).convert("L")

if plain_img.size != enc_img.size:
    raise ValueError("Calibration images must have the same size")

plain_pixels = list(shuffle(plain_img).getdata())
enc_pixels = list(enc_img.getdata())

if len(plain_pixels) % 2 != 0:
    raise ValueError("Pixel count must be even")


blocks = []

prev = IV.copy()

for i in range(0, len(plain_pixels), 2):
    p0 = plain_pixels[i]
    p1 = plain_pixels[i + 1]

    x0 = (p0 + prev[0]) % MOD
    x1 = (p1 + prev[1]) % MOD

    c0 = enc_pixels[i]
    c1 = enc_pixels[i + 1]

    blocks.append(([x0, x1], [c0, c1]))

    prev = [c0, c1]


chosen = None

for i in range(len(blocks)):
    x1, c1 = blocks[i]

    for j in range(i + 1, len(blocks)):
        x2, c2 = blocks[j]
        det = (
            x1[0] * x2[1]
            - x2[0] * x1[1]
        ) % MOD

        if gcd(det, MOD) == 1:
            chosen = (i, j)
            break

    if chosen is not None:
        break


if chosen is None:
    raise ValueError("Could not find invertible calibration blocks")


i, j = chosen

print(f"[+] Using calibration blocks {i} and {j}")

x1, c1 = blocks[i]
x2, c2 = blocks[j]


X = [
    [x1[0], x2[0]],
    [x1[1], x2[1]]
]

C = [
    [c1[0], c2[0]],
    [c1[1], c2[1]]
]



X_inv = matrix_inv_2x2(X)

K = matrix_mul_2x2(C, X_inv)

print("[+] Recovered key:")
print(K[0])
print(K[1])

valid = True

for x, expected_c in blocks:
    calculated_c = matrix_vec_mul(K, x)

    if calculated_c != expected_c:
        valid = False
        break

if not valid:
    raise ValueError("Recovered key failed verification")

print("[+] Key successfully verified against calibration image")



K_inv = matrix_inv_2x2(K)

print("[+] K inverse:")
print(K_inv[0])
print(K_inv[1])



target_img = Image.open(TARGET_ENC).convert("L")
cipher_pixels = list(target_img.getdata())

if len(cipher_pixels) % 2 != 0:
    raise ValueError("Target pixel count must be even")

plain_output = []

prev = IV.copy()

for i in range(0, len(cipher_pixels), 2):
    c0 = cipher_pixels[i]
    c1 = cipher_pixels[i + 1]

    current_cipher = [c0, c1]

    mixed = matrix_vec_mul(K_inv, current_cipher)

    p0 = (mixed[0] - prev[0]) % MOD
    p1 = (mixed[1] - prev[1]) % MOD

    plain_output.append(p0)
    plain_output.append(p1)

    prev = current_cipher


recovered = Image.new("L", target_img.size)
recovered.putdata(plain_output)
unshuffle(recovered).save(OUTPUT)

print(f"[+] Decrypted image saved as {OUTPUT}")
