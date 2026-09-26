# Close Primes

- **Category:** Cryptography
- **Difficulty:** Medium-Hard

---

### Description

Our security intern was tasked with deploying a standard RSA encryption service to safeguard confidential communications. Eager to impress the team with faster key generation, the intern decided to take a clever little "shortcut" during the prime selection process.

The code review did not go well. Told that the modulus was the problem, the intern did **not** touch the prime generation — instead they buried the plaintext under two secret integers `x` and `y` before encrypting, and shipped a single equation as proof that nobody could ever recover them:

> *"Go ahead, solve it. Two unknowns, one equation. I'm sure it's secure enough :)"*

We intercepted the encrypted transmission, the public parameters, and that equation.

### Files

- `chall.py` — the encryption script
- `output.txt` — the intercepted parameters

### Hints

> *"Sometimes the shortest distance between two points reveals everything."*
>
> *"Two unknowns and one equation, yes — but look at what the equation is built out of before you call it unsolvable."*

### Flag Format

`COMPFEST18{...}`
