# Kue 1

**Category:** Cryptography

---

### Description

Ka Fadar adalah seorang chef yang hebat, sekarang ia sedang berusaha membuat kue. bantulah Ka Fadar dalam menciptakan kue tersebut

### Hints

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
