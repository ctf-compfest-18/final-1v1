# Kue 2

**Category:** Cryptography

---

### Description

Kue yang dihasilkan ternyata kurang enak, jadi Ka Fadar ingin menciptakan resep baru dan membuat kue lagi.

### Hints

- The encodings used are the same as Part 1: **Base64**, **Hex**, **Base32**, **Reverse** — plus one **XOR** layer.
- After peeling all the standard encoding layers, you'll hit binary data. That's the XOR layer.
- The XOR key is a **7-letter English word** found at the end of Part 1's flag.
- You **must solve Part 1 first** to obtain the decryption key.

### Flag Format

`COMPFEST18{...}`

### Files

- `ciphertext.txt` — The 50-layer encrypted main course (~31 KB)

### Prerequisites

- Solve **Part 1** ("Layer Cake: Appetizer") first to obtain the decryption key.
