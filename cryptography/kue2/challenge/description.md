# Layer Cake: Main Course (Part 2 of 2)

**Category:** Cryptography
**Difficulty:** Medium
**Points:** 400
**Round:** Qualification

---

### Description

You survived the appetizer? Impressive. Now comes the **main course** — another fifty layers of encoding madness. But there's a twist.

> *"The appetizer always holds the secret ingredient for the main course. Without it, the final layer remains forever sealed."*

Somewhere deep inside this 50-layer cake, there is a **keyed encryption step** (XOR cipher). You'll know you've hit it when peeling a layer produces **binary garbage** instead of a recognizable encoding. The key to unlock it? A word hidden inside Part 1's flag.

### Hints

- This challenge also uses **50 layers** of encoding.
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
