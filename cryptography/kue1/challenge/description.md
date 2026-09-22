# Layer Cake: Appetizer (Part 1 of 2)

**Category:** Cryptography
**Difficulty:** Medium
**Points:** 300
**Round:** Qualification

---

### Description

Welcome to **Chef Crypto's** legendary kitchen! The Chef has gone absolutely mad — taking a simple secret message and burying it beneath an absurd number of encoding layers. We're talking **fifty layers** of culinary encryption.

> *"Every great meal begins with the appetizer. And this appetizer holds a secret ingredient for what comes next... If you can survive the peeling."*

Your task is simple: peel every single layer, one by one, until you reach the hidden message. Each layer uses a well-known encoding technique — nothing exotic, nothing custom. Just... a LOT of them.

Pay close attention to what you find — **the flag from this challenge contains a crucial key needed to unlock Part 2**.

### Hints

- The data has been transformed **50 times** through well-known encoding techniques.
- The encodings used are: **Base64**, **Hex**, **Base32**, **Reverse**, and **ROT13**.
- Each layer is identifiable by its character set:
  - Hex: only `0-9` and `a-f`
  - Base32: only uppercase `A-Z` and digits `2-7`, with `=` padding
  - Base64: mixed case letters, digits, `+`, `/`, and `=` padding
  - Reversed: the `=` padding appears at the **start** instead of the end
  - ROT13: text looks like English but with shifted letters
- Tools like **CyberChef** are your best friend here.

### Flag Format

`COMPFEST18{...}`

### Files

- `ciphertext.txt` — The 50-layer encrypted appetizer (~25 KB)
