# Layer Cake - Writeup

| Challenge Details | Information |
| :--- | :--- |
| **Category** | Cryptography / Classical & Encoding |
| **Difficulty** | Easy-Medium |
| **Time Limit** | 5 minutes |
| **Flag** | `COMPFEST18{l4y3r_by_l4y3r_w3_unr4v3l}` |

---

## 1. Challenge Overview

Participants are provided with a single text file ([`ciphertext.txt`](file:///Users/ghulam/Documents/Fasilkom%20UI/Compfest/Final/tie-round/challenge/ciphertext.txt)) containing an encoded string:

```text
M2QzZDUxNjYzNTRlNTQ2MTMwNTU1NzU5NmYzOTMxNGQ3MTM5NTY1YTdhNzc0NzRlMzUzOTQ2NjI3NjM5NTY1YTdhNzc0NzRlMzU3NDQ4NGY3ODYzNmI1MjUzNGUzMTUxNjE0YTQ1NTU=
```

The accompanying problem description ([`description.md`](file:///Users/ghulam/Documents/Fasilkom%20UI/Compfest/Final/tie-round/challenge/description.md)) provides a thematic narrative about a pastry chef baking a secret message under multiple crusts, accompanied by the hint:
> *"Like an onion, peel each layer to find the truth inside."*

The objective is to identify the sequence of encodings applied to the flag and invert them layer by layer to recover the original flag within the 5-minute tie-breaker window.

---

## 2. Methodology & Pattern Recognition

In timed CTF rounds, quickly recognizing encoding signatures is essential:

1. **Base64 Characteristics**:
   - Character set: `[A-Za-z0-9+/]`
   - String length is typically a multiple of 4.
   - Padded at the end with `=` or `==` (unless URL-safe or unpadded).
2. **Hexadecimal (Base16) Characteristics**:
   - Character set: `[0-9a-fA-F]`
   - Even length (each byte is represented by two hex nibbles).
   - Common ASCII characters typically start with `3`, `4`, `5`, `6`, or `7` in hex (e.g., `0x41` = `'A'`, `0x61` = `'a'`, `0x3d` = `'='`).
3. **Reversal Clues**:
   - Standard Base64 strings end with `=` padding. If padding characters like `==` or `=` appear at the **beginning** of an alphanumeric string, the string has likely been reversed.
4. **ROT13 / Substitution Clues**:
   - Once decoded into readable ASCII, if the text maintains English casing, punctuation, and known flag delimiters (`{` and `}`), but the prefix looks like `PBZCSRFG18{...}`, this indicates a Caesar cipher. Because `P` shifted backward by 13 positions is `C`, `B` shifted by 13 is `O`, and `Z` shifted by 13 is `M`, the text is ROT13 encoded.

---

## 3. Step-by-Step Solution

### Layer 1: Base64 Decoding (Inverting Step 5)

**Input:**
```text
M2QzZDUxNjYzNTRlNTQ2MTMwNTU1NzU5NmYzOTMxNGQ3MTM5NTY1YTdhNzc0NzRlMzUzOTQ2NjI3NjM5NTY1YTdhNzc0NzRlMzU3NDQ4NGY3ODYzNmI1MjUzNGUzMTUxNjE0YTQ1NTU=
```

- **Observation:** The ciphertext consists of alphanumeric characters ending with `=` padding.
- **Action:** Perform standard Base64 decoding.

**Output:**
```text
3d3d5166354e5461305557596f39314d7139565a7a77474e353946627639565a7a77474e3574484f78636b52534e3151614a4555
```

---

### Layer 2: Hexadecimal Decoding (Inverting Step 4)

**Input:**
```text
3d3d5166354e5461305557596f39314d7139565a7a77474e353946627639565a7a77474e3574484f78636b52534e3151614a4555
```

- **Observation:** The string length is 104 (an even number), and all characters are strictly within `[0-9a-f]`. The prefix `3d3d` corresponds to ASCII `==` (`0x3d` is the ASCII value for `=`).
- **Action:** Convert the hex string into raw ASCII bytes.

**Output:**
```text
==Qf5NTa0UWYo91Mq9VZzwGN59Fbv9VZzwGN5tHOxckRSN1QaJEU
```

---

### Layer 3: String Reversal (Inverting Step 3)

**Input:**
```text
==Qf5NTa0UWYo91Mq9VZzwGN59Fbv9VZzwGN5tHOxckRSN1QaJEU
```

- **Observation:** Base64 padding (`==`) appears at the beginning of the string rather than the end. This is a telltale sign that the preceding string was reversed.
- **Action:** Reverse the string characters (`string[::-1]`).

**Output:**
```text
UEJaQ1NSRkcxOHt5NGwzZV9vbF95NGwzZV9qM19oYWU0aTN5fQ==
```

---

### Layer 4: Base64 Decoding (Inverting Step 2)

**Input:**
```text
UEJaQ1NSRkcxOHt5NGwzZV9vbF95NGwzZV9qM19oYWU0aTN5fQ==
```

- **Observation:** The string is now formatted as valid Base64 ending with `==`.
- **Action:** Decode using Base64.

**Output:**
```text
PBZCSRFG18{y4l3e_ol_y4l3e_j3_hae4i3y}
```

---

### Layer 5: ROT13 Substitution (Inverting Step 1)

**Input:**
```text
PBZCSRFG18{y4l3e_ol_y4l3e_j3_hae4i3y}
```

- **Observation:**
  - The format closely mimics the flag structure: `<10 letters>18{...}`.
  - Comparing the expected flag prefix `COMPFEST18{` with `PBZCSRFG18{`:
    - `C` (ASCII 67) + 13 = `P` (ASCII 80)
    - `O` (ASCII 79) + 13 = `B` (ASCII 66, wrapping around modulo 26)
    - `M` (ASCII 77) + 13 = `Z` (ASCII 90)
- **Action:** Apply ROT13 rotation on alphabetic characters.

**Output (Final Flag):**
```text
COMPFEST18{l4y3r_by_l4y3r_w3_unr4v3l}
```

---

## 4. Summary of Layers

| Decoding Step | Operation | Output Sample |
| :--- | :--- | :--- |
| **0. Initial** | Read input | `M2QzZDUxNjYzN...YTQ1NTU=` |
| **1. Invert Step 5** | Base64 Decode | `3d3d5166354e546130555759...` |
| **2. Invert Step 4** | Hex Decode | `==Qf5NTa0UWYo91Mq9...` |
| **3. Invert Step 3** | Reverse String | `UEJaQ1NSRkcxOHt5NGwzZV9v...==` |
| **4. Invert Step 2** | Base64 Decode | `PBZCSRFG18{y4l3e_ol_y4l3e_j3_hae4i3y}` |
| **5. Invert Step 1** | ROT13 Decode | `COMPFEST18{l4y3r_by_l4y3r_w3_unr4v3l}` |

---

## 5. Solver Script

The automated solver is implemented in [`solve.py`](file:///Users/ghulam/Documents/Fasilkom%20UI/Compfest/Final/tie-round/solver/solve.py). Run it using:

```bash
python3 solve.py
```

### Script Implementation ([`solve.py`](file:///Users/ghulam/Documents/Fasilkom%20UI/Compfest/Final/tie-round/solver/solve.py)):

```python
#!/usr/bin/env python3
import base64
import codecs
from pathlib import Path

def main():
    ciphertext_path = Path(__file__).resolve().parent.parent / "challenge" / "ciphertext.txt"
    if ciphertext_path.is_file():
        with open(ciphertext_path, "r", encoding="utf-8") as f:
            ciphertext = f.read().strip()
    else:
        ciphertext = "M2QzZDUxNjYzNTRlNTQ2MTMwNTU1NzU5NmYzOTMxNGQ3MTM5NTY1YTdhNzc0NzRlMzUzOTQ2NjI3NjM5NTY1YTdhNzc0NzRlMzU3NDQ4NGY3ODYzNmI1MjUzNGUzMTUxNjE0YTQ1NTU="

    # Layer 1: Base64
    step1 = base64.b64decode(ciphertext).decode("utf-8")
    # Layer 2: Hex
    step2 = bytes.fromhex(step1).decode("utf-8")
    # Layer 3: Reverse
    step3 = step2[::-1]
    # Layer 4: Base64
    step4 = base64.b64decode(step3).decode("utf-8")
    # Layer 5: ROT13
    flag = codecs.decode(step4, "rot_13")

    print(f"Flag: {flag}")

if __name__ == "__main__":
    main()
```

---

## 6. Alternative CyberChef Recipe

Competitors solving this challenge interactively during the 5-minute tie-breaker can construct a recipe in **CyberChef** with the following operations:
1. `From Base64`
2. `From Hex`
3. `Reverse` (Character mode)
4. `From Base64`
5. `ROT13` (Amount: 13)

---

## 7. Flag

```text
COMPFEST18{l4y3r_by_l4y3r_w3_unr4v3l}
```
