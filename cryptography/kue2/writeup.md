# Layer Cake: Main Course — Writeup (Part 2 of 2)

| Detail | Value |
| :--- | :--- |
| **Challenge** | Layer Cake: Main Course |
| **Category** | Cryptography / Encoding |
| **Difficulty** | Medium |
| **Round** | Qualification |
| **Layers** | **50** (49 encoding + 1 XOR) |
| **XOR Key** | `DESSERT` (from Part 1) |
| **Flag** | `COMPFEST18{m4st3r_ch3f_0f_l4y3r_c4k3s}` |

---

## Challenge Overview

Participants receive a ~3 MB ciphertext file containing data encoded through **50 layers**, similar to Part 1. However, the **innermost layer** is a **XOR cipher** using the key `DESSERT` — extracted from Part 1's flag `COMPFEST18{4pp3t1z3r_k3y_DESSERT}`.

After peeling 48 standard encoding layers, the participant reaches Base64 data that decodes to **non-printable binary bytes** — the XOR-encrypted flag. Using the key from Part 1 completes the decryption.

---

## Encoding Chain (50 Layers)

The flag was encoded in this order (innermost → outermost):

```
xor → base64 → reverse → base64 → base64 → reverse → base64 → reverse
→ base64 → reverse → base64 → reverse → base64 → reverse → base64
→ reverse → base64 → reverse → hex → reverse → base64 → base32 → reverse
→ base64 → base32 → reverse → base64 → reverse → hex → reverse → base64
→ reverse → base64 → reverse → base64 → reverse → base64 → reverse
→ base64 → reverse → base64 → reverse → base64 → base64 → reverse
→ base64 → reverse → base64 → reverse → base64
```

**Layer breakdown:** 21 × Base64, 24 × Reverse, 2 × Hex, 2 × Base32, 1 × XOR

---

## Prerequisite: The Key

From Part 1's flag: `COMPFEST18{4pp3t1z3r_k3y_DESSERT}`

- `k3y` = "key" in leetspeak
- `DESSERT` = the 7-byte XOR key (ASCII: `44 45 53 53 45 52 54`)

---

## Solving Strategy

### Steps 1-48: Standard Peeling

Same as Part 1 — identify each layer by character set and peel:

1. See Base64 → `From Base64`
2. See `=...` → `Reverse`
3. Repeat 48 times total...

### Step 49: The XOR Wall

After 48 peeling steps, you decode a Base64 string and get **binary garbage**:
```
hex: 070a1e0303170710746b282866273076210c263a67221a63...
```

This is NOT another encoding — it's the **XOR-encrypted flag**.

### Step 50: XOR Decryption

In CyberChef:
1. Add `From Base64` (the last base64 layer)
2. Add `XOR` with key `DESSERT` (UTF-8)

Or in Python:
```python
key = b"DESSERT"
flag = bytes([data[i] ^ key[i % 7] for i in range(len(data))])
```

**Verification** — first 7 bytes:

| Position | Cipher | Key | XOR | Char |
|---|---|---|---|---|
| 0 | `0x07` | `D` (0x44) | `0x43` | **C** |
| 1 | `0x0a` | `E` (0x45) | `0x4f` | **O** |
| 2 | `0x1e` | `S` (0x53) | `0x4d` | **M** |
| 3 | `0x03` | `S` (0x53) | `0x50` | **P** |
| 4 | `0x03` | `E` (0x45) | `0x46` | **F** |
| 5 | `0x17` | `R` (0x52) | `0x45` | **E** |
| 6 | `0x07` | `T` (0x54) | `0x53` | **S** |

First 7 bytes decode to `COMPFES` — key confirmed! ✓

---

## Solver Script

See [`solver/solve.py`](solver/solve.py) — run with:

```bash
python3 solver/solve.py
```

**Output** (last 5 lines):
```
  Step 47 | Hex decode     |       52 chars | =4iN39jZmwQI21DY+oRNjphInpjJMEidwci...
  Step 48 | Reverse        |       52 chars | BwoeAwMXBxB0aygoZicwdiEMJjpnIhpjNRo+...
  Step 49 | Base64 + XOR   |       38 chars | COMPFEST18{m4st3r_ch3f_0f_l4y3r_c4k3s}
[✓] Solved in 49 steps!
```

---

## CyberChef Recipe (Full)

For the manual approach, build a recipe with these 50 operations in order:

1-48: Alternating `From Base64`, `Reverse`, `From Hex`, `From Base32` (following the chain above in reverse)

49: `From Base64`

50: `XOR` → Key: `DESSERT`, Key format: UTF-8

---

## Flag

```
COMPFEST18{m4st3r_ch3f_0f_l4y3r_c4k3s}
```
