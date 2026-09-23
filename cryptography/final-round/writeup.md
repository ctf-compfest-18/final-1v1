# Close Primes - Writeup

| Challenge Details | Information |
| :--- | :--- |
| **Category** | Cryptography / Asymmetric Cryptography |
| **Difficulty** | Medium |
| **Time Limit** | 20 minutes |
| **Flag** | `COMPFEST18{f3rm4t_kn3w_cl0s3_pr1m3s_4r3_w34k}` |

---

## 1. Challenge Overview

Participants are provided with two challenge files:
1. [`chall.py`](file:///Users/ghulam/Documents/Fasilkom%20UI/Compfest/Final/final-round-1/challenge/chall.py): The Python encryption script showing how the RSA parameters were used to encrypt the flag.
2. [`output.txt`](file:///Users/ghulam/Documents/Fasilkom%20UI/Compfest/Final/final-round-1/challenge/output.txt): The intercepted output containing the modulus $n$, public exponent $e$, and ciphertext $c$.

### Given Parameters

```text
n = 44942328371557897693232629769725637345551773958969975534088096274272083536335143799228617197785844127567407916538857486445961455835625282540606289553029998469410132520785709219197898958320171233568760214259630711496059533969940857206676158286130674482846747069751384571736770610246782499744958776186079350229
e = 65537
c = 66006869579140731428384347236188952231617497245010983041089142524224256062733795090765977689519901227368638180534413595841214484179796158579405971097390247090739376386764222455613758417294820147584378104616030063205704404454715075356301134044424240326220773877236907940799379765778531683709768627762829226
```

### Problem Scenario & Clues

In [`description.md`](file:///Users/ghulam/Documents/Fasilkom%20UI/Compfest/Final/final-round-1/challenge/description.md), we learn that an eager intern deployed RSA encryption but took a "shortcut" in generating the primes:
> *"I made my own prime generation... I'm sure it's secure enough :)"*

Additionally, the challenge description includes the following hint:
> *"Sometimes the shortest distance between two points reveals everything."*

In public key cryptography, a "shortcut" where the "distance between two points" is small refers to choosing the prime factors $p$ and $q$ **extremely close to each other** ($|p - q| \ll \sqrt{n}$). This flaw makes the modulus $n$ critically vulnerable to **Fermat's Factorization Method**.

---

## 2. Vulnerability Analysis: Why Close Primes Break RSA

In textbook RSA, security depends on the hardness of factoring a composite modulus $n = p \cdot q$. When $p$ and $q$ are chosen independently and uniformly at random from large primes of equal bit length, state-of-the-art general-purpose algorithms like the **General Number Field Sieve (GNFS)** require sub-exponential time:

$$O\left(\exp\left( \left(\sqrt[3]{\frac{64}{9}} + o(1)\right) (\ln n)^{1/3} (\ln \ln n)^{2/3} \right)\right)$$

For 1024-bit moduli, GNFS would take months on high-performance compute clusters.

### The Geometric vs. Arithmetic Mean Trap

When $p$ and $q$ are close to each other, their arithmetic mean is almost indistinguishable from their geometric mean:

$$\frac{p + q}{2} \approx \sqrt{p \cdot q} = \sqrt{n}$$

Let $p$ and $q$ be odd primes with $q > p$. Define:

$$a = \frac{p + q}{2}, \quad b = \frac{q - p}{2}$$

Because both $p$ and $q$ are odd, their sum and difference are even, so $a$ and $b$ are integers. We can express $p$ and $q$ in terms of $a$ and $b$:

$$p = a - b, \quad q = a + b$$

Multiplying $p$ and $q$ gives:

$$n = p \cdot q = (a - b)(a + b) = a^2 - b^2$$

Rearranging this identity:

$$a^2 - n = b^2$$

Because $b^2 \ge 0$, we have $a \ge \lceil \sqrt{n} \rceil$.

Now consider the difference $a - \sqrt{n}$:

$$\sqrt{n} = \sqrt{a^2 - b^2} = a \sqrt{1 - \frac{b^2}{a^2}} \approx a \left(1 - \frac{b^2}{2a^2}\right) = a - \frac{b^2}{2a}$$

Hence:

$$a - \sqrt{n} \approx \frac{b^2}{2a} \approx \frac{(q - p)^2}{8\sqrt{n}}$$

### Condition for Instant Factorization ($0$ Iterations)

If $|q - p| < 2 \cdot n^{1/4}$, then:

$$\frac{(q - p)^2}{8\sqrt{n}} < \frac{4\sqrt{n}}{8\sqrt{n}} = \frac{1}{2}$$

Because $\frac{b^2}{2a} < \frac{1}{2}$, rounding up yields:

$$a = \lceil \sqrt{n} \rceil$$

When this condition is satisfied, $a^2 - n$ is an **exact square on the very first attempt** ($a = \lceil\sqrt{n}\rceil$). The modulus is factored instantaneously with zero search iterations!

---

## 3. Fermat's Factorization Algorithm

Pierre de Fermat's 1643 factorization method exploits the representation of an odd composite number as the difference of two squares: $n = a^2 - b^2$.

### Algorithm

1. Initialize candidate $a = \lceil \sqrt{n} \rceil$.
2. Compute $\Delta = a^2 - n$.
3. Check if $\Delta$ is a square:
   - Compute $b = \lfloor \sqrt{\Delta} \rfloor = \text{isqrt}(\Delta)$.
   - Check if $b^2 == \Delta$.
4. If $b^2 == \Delta$:
   - Set $p = a - b$ and $q = a + b$.
   - Output $(p, q)$ and terminate.
5. If not, increment $a \leftarrow a + 1$ and return to Step 2.

### Analysis on the Challenge Modulus

In this challenge:
- $n \approx 4.49 \times 10^{307}$ (1023 bits)
- $\sqrt{n} \approx 6.70 \times 10^{153}$
- $p$ and $q$ differ by $q - p = 1,013,668,572 \approx 10^9$
- $b = \frac{q - p}{2} = 506,834,286$
- $b^2 = 256,880,993,465,129,796 \approx 2.57 \times 10^{17}$

Comparing $b^2$ with $2\sqrt{n}$:

$$b^2 \approx 2.57 \times 10^{17} \ll 2\sqrt{n} \approx 1.34 \times 10^{154}$$

Because $(a - 1)^2 = a^2 - 2a + 1 < a^2 - b^2 = n < a^2$, we have:

$$\lceil \sqrt{n} \rceil = a$$

Consequently, Fermat's method identifies the factors at **iteration 0** within a fraction of a millisecond.

---

## 4. Step-by-Step Solution with Exact Values

### Step 1: Compute $a = \lceil \sqrt{n} \rceil$

Using Python's built-in `math.isqrt`:

```python
import math

a = math.isqrt(n)
if a * a < n:
    a += 1
```

Value of $a$:
```text
a = 6703903964971298549787012499102924481204972448254168472572572803398595616708693312243200493876332803758231553138066346839008210339789110853482192675951995
```

### Step 2: Compute $b^2 = a^2 - n$ and $b = \sqrt{b^2}$

```python
b2 = a * a - n
b = math.isqrt(b2)
assert b * b == b2
```

Values:
```text
b2 = 256880993465129796
b  = 506834286
```

Because $506834286^2 = 256880993465129796$, $b^2$ is an exact square!

### Step 3: Recover $p$ and $q$

$$p = a - b$$
$$q = a + b$$

```text
p = 6703903964971298549787012499102924481204972448254168472572572803398595616708693312243200493876332803758231553138066346839008210339789110853482192169117709
q = 6703903964971298549787012499102924481204972448254168472572572803398595616708693312243200493876332803758231553138066346839008210339789110853482193182786281
```

Verification:
- $p \cdot q = n \quad \checkmark$
- Gap $q - p = 2b = 1,013,668,572 \approx 2^{30} \quad \checkmark$
- Both $p$ and $q$ are 512-bit primes.

### Step 4: Compute Euler's Totient $\phi(n)$

$$\phi(n) = (p - 1)(q - 1) = n - (p + q) + 1 = n - 2a + 1$$

```text
phi = 44942328371557897693232629769725637345551773958969975534088096274272083536335143799228617197785844127567407916538857486445961455835625282540606289553029985061602202578188609645172900752471208823623863705922685566350452736778707439820051671885142921817239230606645108439043092593826102921523251811800727446240
```

### Step 5: Compute Private Exponent $d$

$$d \equiv e^{-1} \pmod{\phi(n)}$$

Using Python 3's built-in modular inverse `pow(e, -1, phi)`:

```text
d = 32277118449005708662664959000281463884224650147257256335176442550581174418850764428370119997335613644145181436679294813190083674920597689833548328984879004789347887009630918088697958292526585850898393532056227234035477812757681947258040375548009628821792515772671497993635355329145475262985129259469256136833
```

### Step 6: Decrypt the Ciphertext

$$m = c^d \pmod n$$

```text
m = 617499489106135659649779678104747846926214826555743549582381576250819684320480853989994811811939968529755005
```

Converting $m$ to hexadecimal bytes:
```text
m_hex = 434f4d504645535431387b6633726d34745f6b6e33775f636c3073335f7072316d33735f3472335f7733346b7d
m_bytes = bytes.fromhex(m_hex)
```

Resulting ASCII string:
```text
COMPFEST18{f3rm4t_kn3w_cl0s3_pr1m3s_4r3_w34k}
```

---

## 5. Solver Script

The complete standalone solver is implemented in [`solve.py`](file:///Users/ghulam/Documents/Fasilkom%20UI/Compfest/Final/final-round-1/solver/solve.py). It requires no external dependencies and automatically reads the public parameters from [`output.txt`](file:///Users/ghulam/Documents/Fasilkom%20UI/Compfest/Final/final-round-1/challenge/output.txt):

```python
#!/usr/bin/env python3
"""
Close Primes - Solver Script
CTF: COMPFEST 18 (Final Round)
Category: Cryptography
"""

import math
import re
from pathlib import Path


def fermat_factorization(n: int):
    """
    Fermat's Factorization Method:
    n = a^2 - b^2 = (a - b)(a + b) = p * q
    When p and q are close, a = (p + q) // 2 is very close to ceil(sqrt(n)).
    """
    a = math.isqrt(n)
    if a * a < n:
        a += 1

    iterations = 0
    while True:
        b2 = a * a - n
        b = math.isqrt(b2)
        if b * b == b2:
            p = a - b
            q = a + b
            return p, q, iterations
        a += 1
        iterations += 1


def main():
    # 0. Load challenge parameters from output.txt or use fallback constants
    output_path = Path(__file__).resolve().parent.parent / "challenge" / "output.txt"
    n, e, c = None, None, None

    if output_path.is_file():
        content = output_path.read_text(encoding="utf-8")
        n_match = re.search(r"n\s*=\s*(\d+)", content)
        e_match = re.search(r"e\s*=\s*(\d+)", content)
        c_match = re.search(r"c\s*=\s*(\d+)", content)
        if n_match and e_match and c_match:
            n = int(n_match.group(1))
            e = int(e_match.group(1))
            c = int(c_match.group(1))

    if n is None or e is None or c is None:
        n = 44942328371557897693232629769725637345551773958969975534088096274272083536335143799228617197785844127567407916538857486445961455835625282540606289553029998469410132520785709219197898958320171233568760214259630711496059533969940857206676158286130674482846747069751384571736770610246782499744958776186079350229
        e = 65537
        c = 66006869579140731428384347236188952231617497245010983041089142524224256062733795090765977689519901227368638180534413595841214484179796158579405971097390247090739376386764222455613758417294820147584378104616030063205704404454715075356301134044424240326220773877236907940799379765778531683709768627762829226

    print("=" * 60)
    print("Close Primes - Automated Solver")
    print("=" * 60)
    print(f"[*] Modulus n ({n.bit_length()} bits): {n}\n")
    print(f"[*] Public Exponent e: {e}\n")
    print(f"[*] Ciphertext c: {c}\n")

    # Step 1: Fermat Factorization
    print("[*] Starting Fermat's factorization...")
    p, q, iters = fermat_factorization(n)
    if p > q:
        p, q = q, p

    print(f"[+] Factorization complete in {iters} iterations!")
    print(f"[+] p ({p.bit_length()} bits): {p}")
    print(f"[+] q ({q.bit_length()} bits): {q}")
    print(f"[+] Gap (q - p): {q - p}")

    # Verify factorization
    assert p * q == n, "Factorization verification failed!"
    print("[+] Verified: p * q == n ✓\n")

    # Step 2: Compute Euler's Totient phi(n) and Private Exponent d
    phi = (p - 1) * (q - 1)
    d = pow(e, -1, phi)
    print(f"[+] phi(n) = {phi}")
    print(f"[+] d = {d}\n")

    # Step 3: Decrypt Ciphertext
    m = pow(c, d, n)
    print(f"[+] Decrypted integer m: {m}")

    flag_bytes = m.to_bytes((m.bit_length() + 7) // 8, byteorder="big")
    flag = flag_bytes.decode("utf-8")

    print("\n" + "=" * 60)
    print(f"[*] FLAG: {flag}")
    print("=" * 60)

    # Validate flag
    assert flag == "COMPFEST18{f3rm4t_kn3w_cl0s3_pr1m3s_4r3_w34k}", "Flag verification failed!"
    print("[*] Verification successful: Flag captured!")


if __name__ == "__main__":
    main()
```

### Running the Solver

```bash
python3 solver/solve.py
```

### Execution Output

```text
============================================================
Close Primes - Automated Solver
============================================================
[*] Modulus n (1023 bits): 44942328371557897693232629769725637345551773958969975534088096274272083536335143799228617197785844127567407916538857486445961455835625282540606289553029998469410132520785709219197898958320171233568760214259630711496059533969940857206676158286130674482846747069751384571736770610246782499744958776186079350229

[*] Public Exponent e: 65537

[*] Ciphertext c: 66006869579140731428384347236188952231617497245010983041089142524224256062733795090765977689519901227368638180534413595841214484179796158579405971097390247090739376386764222455613758417294820147584378104616030063205704404454715075356301134044424240326220773877236907940799379765778531683709768627762829226

[*] Starting Fermat's factorization...
[+] Factorization complete in 0 iterations!
[+] p (512 bits): 6703903964971298549787012499102924481204972448254168472572572803398595616708693312243200493876332803758231553138066346839008210339789110853482192169117709
[+] q (512 bits): 6703903964971298549787012499102924481204972448254168472572572803398595616708693312243200493876332803758231553138066346839008210339789110853482193182786281
[+] Gap (q - p): 1013668572
[+] Verified: p * q == n ✓

[+] phi(n) = 44942328371557897693232629769725637345551773958969975534088096274272083536335143799228617197785844127567407916538857486445961455835625282540606289553029985061602202578188609645172900752471208823623863705922685566350452736778707439820051671885142921817239230606645108439043092593826102921523251811800727446240
[+] d = 32277118449005708662664959000281463884224650147257256335176442550581174418850764428370119997335613644145181436679294813190083674920597689833548328984879004789347887009630918088697958292526585850898393532056227234035477812757681947258040375548009628821792515772671497993635355329145475262985129259469256136833

[+] Decrypted integer m: 617499489106135659649779678104747846926214826555743549582381576250819684320480853989994811811939968529755005

============================================================
[*] FLAG: COMPFEST18{f3rm4t_kn3w_cl0s3_pr1m3s_4r3_w34k}
============================================================
[*] Verification successful: Flag captured!
```

---

## 6. Flag

```text
COMPFEST18{f3rm4t_kn3w_cl0s3_pr1m3s_4r3_w34k}
```

---

## 7. Educational Note: RSA Security Requirements & Modern Standards

This challenge highlights the critical importance of secure prime generation in RSA.

When developers attempt to optimize prime generation—such as finding a prime $p$ and then searching for $q$ starting near $p$—the arithmetic mean $\frac{p+q}{2}$ directly equals $\lceil\sqrt{n}\rceil$, reducing the factorization problem to taking a single integer square root.

### Cryptographic Standards on Prime Separation

To ensure resilience against Fermat's factorization and related lattice-based attacks, modern standards mandate a minimum separation distance between primes:

1. **NIST FIPS 186-4 & FIPS 186-5 (Digital Signature Standard)**:
   Section B.3.3 requires that the two prime factors satisfy:
   $$|p - q| > 2^{nlen/2 - 100}$$
   For a 1024-bit modulus ($nlen = 1024$):
   $$|p - q| > 2^{512 - 100} = 2^{412} \approx 10^{124}$$
   In this challenge, $|p - q| \approx 10^9 \approx 2^{30}$, which is smaller than the NIST minimum threshold by over **380 orders of magnitude**.

2. **ANSI X9.31 Standard**:
   Mandates that prime factors $p$ and $q$ be generated independently from cryptographically strong random seeds, with explicit checks that $|p - q| > 2^{nlen/2 - 100}$.

### Key Recommendations

- **Never create custom prime generators**: Rely exclusively on established cryptographic libraries (such as OpenSSL or `cryptography` in Python).
- **Independent generation**: Primes $p$ and $q$ must always be drawn from independent calls to a cryptographically secure pseudo-random number generator (CSPRNG).
- **Key sizing**: Modern production deployments should use at least 2048-bit or 3072-bit moduli along with modern padding schemes like OAEP.
