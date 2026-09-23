# Varnish

- **Category:** Cryptography
- **Difficulty:** Hard

---

### Description

Someone on the team read that a *polished* RSA implementation should never let the
private exponent escape, so they varnished theirs: the top of `d` was scraped off
before publishing, and the plaintext was buried under two nonsense integers `x` and `y`
that appear nowhere in the key material.

Almost nowhere.

The only other thing they shipped was a cubic diophantine equation in those same
`x` and `y` — "unsolvable without the flag anyway," they said.

We intercepted the varnish job. Two coats, one secret.

### Files

- `chall.py` — the script that produced the parameters
- `output.txt` — everything that was published

### Hint

> A quarter of a private exponent is a generous tip.
> And before you go hunting for divisors: count what the equation is *made of*.

### Flag Format

`COMPFEST18{...}`
