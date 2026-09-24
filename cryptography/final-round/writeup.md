# Close Primes (Diophantine edition) - Writeup

| Challenge Details | Information |
| :--- | :--- |
| **Category** | Cryptography / Asymmetric Cryptography |
| **Difficulty** | Medium-Hard |
| **Suggested Time Limit** | 30 minutes |
| **Flag** | `COMPFEST18{f3rm4t_kn3w_cl0s3_pr1m3s_4r3_w34k}` |

> This is the original **Close Primes** soal with a diophantine layer added on top.
> The RSA half is untouched: same 512-bit close primes, same modulus `n`, same `e`,
> same flag, same 0-iteration Fermat factorisation. What changed is that the plaintext
> is now masked by two secret integers `x, y`, and the only thing published about them
> is one quadratic equation.

---

## 1. Challenge Overview

Participants receive `chall.py` and `output.txt`:

```python
p, q = generate_primes(512)

n = p * q
e = 65537

x = random.randrange(p // 10, p // 9)
y = random.randrange(p // 10, p // 9)

alpha = p - (3 * x + y)
beta = q - (2 * x + y)

A = 2 * alpha + 3 * beta
B = alpha + beta
b = 6 * x**2 + 5 * x * y + y**2 + A * x + B * y

m = bytes_to_long(FLAG)
c = pow(x**2 + m + y, e, n)
```

Note what the ciphertext actually is: recovering $d$ and computing $c^d \bmod n$ gives

$$x^2 + m + y,$$

**not** the flag. Factoring $n$ is necessary but no longer sufficient - the two integers
$x$ and $y$ have to be pinned down exactly, and the only information published about them
is the last line of `output.txt`:

$$6x^2 + 5xy + y^2 + A\,x + B\,y = b .$$

One equation, two unknowns, all three constants ~512-1022 bits. Brute force is hopeless
and the intern is technically right that a generic diophantine of this shape is
underdetermined. The way in is that this particular one is not generic.

---

## 2. Step 1: the quadratic part factors

Look at the homogeneous part alone:

$$6x^2 + 5xy + y^2 .$$

Its discriminant as a quadratic in $y$ is $25x^2 - 24x^2 = x^2$ - a perfect square, so it
splits over $\mathbb{Z}$:

$$6x^2 + 5xy + y^2 = (3x + y)(2x + y).$$

That is the whole hint in the description: *look at what the equation is built out of*.

## 3. Step 2: complete the product

If the quadratic part is a product of two linear forms, the natural move is to try to
absorb the linear terms into the same product. Take unknown constants $\alpha, \beta$:

$$(3x + y + \alpha)(2x + y + \beta) = 6x^2 + 5xy + y^2 + (2\alpha + 3\beta)x + (\alpha + \beta)y + \alpha\beta .$$

Matching the published coefficients gives a $2 \times 2$ linear system

$$A = 2\alpha + 3\beta, \qquad B = \alpha + \beta,$$

whose determinant is $2 \cdot 1 - 3 \cdot 1 = -1$, so it has exactly one integer solution:

$$\boxed{\ \alpha = 3B - A, \qquad \beta = A - 2B\ }$$

Both come out as clean 511-bit positive integers, which is already a strong signal that
this reading of the equation is the intended one.

## 4. Step 3: the equation *is* the modulus

Adding $\alpha\beta$ to both sides of the challenge equation turns it into a product:

$$(3x + y + \alpha)\,(2x + y + \beta) \;=\; b + \alpha\beta .$$

Compute the right-hand side and compare it with the public modulus:

$$b + \alpha\beta \;=\; n .$$

That is the pivot of the challenge. The equation is a **factorisation of $n$ in disguise**:
the two bracketed values are $p$ and $q$ themselves,

$$p = 3x + y + \alpha, \qquad q = 2x + y + \beta .$$

So solving the diophantine is exactly as hard as factoring $n$ - which, in this soal, is
the one thing we already know how to do.

## 5. Step 4: Fermat, unchanged from the original soal

The intern never fixed the prime generation, so $p$ and $q$ still sit next to each other:

$$q - p = 1013668572 \approx 2^{29.9}.$$

With $a = \lceil \sqrt{n} \rceil$, the value $a^2 - n$ is a perfect square immediately, so
Fermat's method returns the factors in **0 iterations**. The blow-by-blow analysis from
the original release (preserved in `final-round-backup-20260924/writeup.md`) applies
verbatim, because the modulus here is byte-identical to it.

```text
p = 6703903964971298549787012499102924481204972448254168472572572803398595616708693312243200493876332803758231553138066346839008210339789110853482192169117709
q = 6703903964971298549787012499102924481204972448254168472572572803398595616708693312243200493876332803758231553138066346839008210339789110853482193182786281
```

## 6. Step 5: back out x and y

The two brackets are $p$ and $q$, but nothing says which is which, so try both
orientations. With $s_3 = 3x + y$ and $s_2 = 2x + y$:

$$s_3 = P - \alpha, \qquad s_2 = Q - \beta, \qquad x = s_3 - s_2, \qquad y = 3s_2 - 2s_3 .$$

Both orientations happen to yield positive integer solutions here - the diophantine
genuinely has two - so keep both and let the mask decide.

```text
x = 714409550171505199264149331076308336710665897491930876508819297899297515796656445885974794839134851342025294376963715146803736413597929619443007860946393
y = 696408622439587404369480810217586124857004552206231624494911652709700280462710473385862720325965414339124631214866299493506224670800623922662495013198901
```

## 7. Step 6: strip the mask

Standard RSA from here, plus one subtraction:

$$\varphi(n) = (p-1)(q-1), \qquad d = e^{-1} \bmod \varphi(n), \qquad m = \left(c^{d} \bmod n\right) - x^2 - y .$$

The mask $x^2 + m + y$ is not symmetric in $x$ and $y$, so only one of the candidate pairs
(and one orientation of it) produces printable ASCII:

```text
COMPFEST18{f3rm4t_kn3w_cl0s3_pr1m3s_4r3_w34k}
```

---

## 8. Solver

`solver/solve.py` runs the whole chain in **0.03 s** and needs nothing but the standard
library (no SageMath, no pycryptodome):

```bash
python3 solver/solve.py
```

```text
[*] Step 1: 6x^2 + 5xy + y^2 = (3x + y)(2x + y)
[+] alpha = 3B - A  (511 bits)
[+] beta  = A - 2B  (511 bits)
[*] Step 2: is b + alpha*beta the modulus?  True
[+] (3x + y + alpha) * (2x + y + beta) = n  -> the two factors of n
[*] Step 3: Fermat's factorization (0 iterations)
[+] gap q - p = 1013668572  (~2^29)
[*] Step 4: 2 positive integer solution(s) of the diophantine
[*] FLAG: COMPFEST18{f3rm4t_kn3w_cl0s3_pr1m3s_4r3_w34k}
```

---

## 9. Design notes for organisers

**What was kept identical.** `n`, `e`, `p`, `q`, the flag, and the close-prime weakness.
Only `c` changed (it is now the masked plaintext) and one line was appended to
`output.txt`. The Fermat sections of the original writeup remain correct verbatim.

**Why $x, y \approx p/10$.** The sizes are the security-relevant choice. Publishing $A$ and
$B$ publishes $\alpha$ and $\beta$, and $p = (3x+y) + \alpha$ - so $\alpha$ is a known
*approximation* of $p$. If $x, y$ were small, the unknown part $3x+y$ would fall below
$n^{1/4} = 2^{255}$ and Coppersmith's known-MSB attack would factor $n$ straight from the
equation, bypassing the whole soal. With $x, y \approx p/10$ the unknown part is
$3x + y \approx 0.4p$ (510 bits), far above that bound.

**Why coefficients $(6, 5, 1)$.** The form has to factor over $\mathbb{Z}$ (discriminant
$x^2$) and the coefficient system $\{A = 2\alpha + 3\beta,\ B = \alpha + \beta\}$ has
determinant $-1$, so $\alpha, \beta$ come out as integers with no divisibility side
conditions. Swapping in e.g. $(3x+4y)(5x+y)$ works too but leaves a determinant of 17 and
a fussier recovery step.

**Two solutions.** The diophantine really does have two positive integer solutions, one per
orientation of $(p, q)$. This is intentional and mirrors the classic *Polish* (CryptoCTF
2021) ending: the asymmetric mask $x^2 + m + y$ is what disambiguates, so solvers must try
both rather than assume.

**Regenerating.** `challenge/secret.py` holds the flag and the frozen prime pair. Run
`python3 chall.py > output.txt` from `challenge/` to mint a new instance ($x, y$ are random
each run); pass `fresh=True` in `generate_primes` to also draw new close primes. Then
rebuild the attachment:

```bash
cd challenge && 7z a -tzip -mem=AES256 -p'<password>' ../public/challenge.zip chall.py output.txt
cd ../public && shasum -a 256 challenge.zip > SHA256SUMS.txt
```

**Attachment.** Participants get `public/challenge.zip` only - AES-256 encrypted, holding
just `chall.py` and `output.txt`. The password lives in `README.md` at the challenge root
(same convention as the other soal), and `public/SHA256SUMS.txt` carries its digest.
`challenge/` is the authoring copy and must never be shipped: it contains `secret.py`.

**Difficulty.** The factoring is still free (0 Fermat iterations); the added work is purely
algebraic - spot the factorable form, complete the product, recognise $b + \alpha\beta = n$.
That lifts the soal from Medium to Medium-Hard without adding any compute.
