# Layer Cake: Appetizer — Writeup (Part 1 of 2)

| Detail | Value |
| :--- | :--- |
| **Challenge** | Layer Cake: Appetizer |
| **Category** | Cryptography / Encoding |
| **Difficulty** | Medium |
| **Round** | Qualification |
| **Layers** | **50** |
| **Flag** | `COMPFEST18{4pp3t1z3r_k3y_DESSERT}` |

---

## Challenge Overview

Participants receive a ~854 KB ciphertext file containing data that has been encoded **50 times** through a chain of well-known encoding techniques. The problem description reveals the encoding types used (Base64, Hex, Base32, Reverse, ROT13) and hints that the flag contains a key for Part 2.

---

## Encoding Chain (50 Layers)

The flag was encoded in this order (innermost → outermost):

```
rot13 → reverse → base64 → reverse → base64 → reverse → base64 → base64
→ reverse → base64 → hex → reverse → base64 → base64 → reverse → base64
→ reverse → base64 → reverse → base64 → reverse → base64 → reverse
→ base64 → reverse → base64 → reverse → base32 → reverse → base64
→ base32 → reverse → base64 → base64 → reverse → hex → reverse → base64
→ reverse → base64 → reverse → base64 → reverse → base64 → reverse
→ base64 → reverse → base64 → reverse → base64
```

**Layer breakdown:** 21 × Base64, 24 × Reverse, 2 × Hex, 2 × Base32, 1 × ROT13

---

## How to Identify Each Layer

When peeling layers in CyberChef, use these identification rules:

| If you see... | It's... | CyberChef operation |
|---|---|---|
| Starts with `=` or `==` | **Reversed** | `Reverse` |
| Only chars `0-9` and `a-f` | **Hex encoded** | `From Hex` |
| Only chars `A-Z`, `2-7`, `=` | **Base32 encoded** | `From Base32` |
| Mixed case + digits + `+/=` | **Base64 encoded** | `From Base64` |
| Text like `PBZCSRFG18{...}` | **ROT13** (final layer) | `ROT13` |

### The Pattern

The chain heavily alternates between **Base64** and **Reverse**:
```
... → base64 → reverse → base64 → reverse → base64 → ...
```

This means most of the 50 clicks follow a repetitive pattern:
1. See `=...` at start → click `Reverse`
2. See Base64 text → click `From Base64`
3. Repeat

Occasional **Hex** and **Base32** layers break the pattern, but they're easy to spot by their character sets.

---

## Solving Strategy

### Option A: CyberChef (Manual — ~15 min)

1. Open [CyberChef](https://gchq.github.io/CyberChef/)
2. Paste the ciphertext
3. Identify the outermost layer and add the corresponding decode operation
4. Repeat 50 times until the flag appears

### Option B: Python Auto-Peeler (Instant)

```python
import base64, codecs

def auto_peel(data):
    if data.startswith('='):           return data[::-1], 'Reverse'
    if all(c in '0123456789abcdef' for c in data) and len(data) % 2 == 0:
        return bytes.fromhex(data).decode('latin-1'), 'Hex'
    if all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567=' for c in data):
        return base64.b32decode(data).decode('latin-1'), 'Base32'
    try:
        return base64.b64decode(data).decode('latin-1'), 'Base64'
    except: pass
    return codecs.decode(data, 'rot_13'), 'ROT13'

data = open('ciphertext.txt').read().strip()
step = 0
while 'COMPFEST18{' not in data:
    step += 1
    data, name = auto_peel(data)
    print(f"Step {step}: {name}")
print(f"FLAG: {data}")
```

---

## Solver Script

See [`solver/solve.py`](solver/solve.py) — run with:

```bash
python3 solver/solve.py
```

**Output** (last 3 lines):
```
  Step 49 | Base64 decode  |       33 chars | PBZCSRFG18{4cc3g1m3e_x3l_QRFFREG}
  Step 50 | ROT13          |       33 chars | COMPFEST18{4pp3t1z3r_k3y_DESSERT}
[✓] Solved in 50 steps!
[!] Key for Part 2: DESSERT
```

---

## Flag

```
COMPFEST18{4pp3t1z3r_k3y_DESSERT}
```

> [!IMPORTANT]
> The word **`DESSERT`** at the end of the flag is the XOR key needed for Part 2!
