# Varnish - Writeup

| Challenge Details | Information |
| :--- | :--- |
| **Category** | Cryptography / Asymmetric Cryptography |
| **Difficulty** | Hard |
| **Suggested Time Limit** | 45 minutes |
| **Flag** | `COMPFEST18{s3c0nd_c04t_0f_v4rn1sh_st1ll_cr4cks_wh3n_d_l34ks_1ts_l0w_b1ts}` |

> Lineage: this challenge is a re-cut of **Polish** (CryptoCTF 2021). The scaffolding
> (a masked plaintext, a partially leaked $d$, a cubic diophantine) is deliberately
> familiar; the **equation is different**, so the hidden identity, the shape of the
> second factor, and the long division all have to be re-derived from scratch.
> A team that memorised `4a^3 + b = n` gets the wrong number here.

---

## 1. Challenge Overview

Participants receive two files:

1. `chall.py` - the generator that produced the parameters.
2. `output.txt` - everything that was published.

### Given Parameters

```text
m = bytes_to_long(flag)
e = 257
n = p * q = 570336775345500704123184569217170483758255113580628721144688594787413077399873119012814006815635322510135961585525305625677032485593044979419322194782011649747192653776694393401635336089990614077627207417722106078600597066800281848153979760729153849708134686041832292487383
d = 0b1[REDACTED]110001110101001110011001101101010111011100011100011100111000110100010001001100110010001000010011101001011101111001011000000001010101110010011110101010100110011010110000111100010110111000001001001101011100110000010111111011010011100101110001
c = pow(x**2 + m + y, e, n) = 271161046556824626722925064854792313715442510058908088877782919111317413166650372892092221740019231349507668126605043975071174117851329558152857861792460089002766112159393328487265121974581860734019531733232559674541546572061015880890978198320938283446810809594402737691997
x**3 + y**3 + 4*x*y*(x + y) - 1352576970205713513938943831840123066787249439725305386457235929053682164104515220737951412*(x**2 + y**2) = 540642877383260435849671929824601164165450658606486190005159781864957204541096847276644444628475907315404435158263564282759836523466825164559080099901930698076265179099749489972604042329867917708911042977747638916715957788931990503152012122623463749017867745829636657689047
```

So we are handed:

- $n$ (907 bits), $e = 257$, and $c$;
- the **low 240 bits of $d$** (the high bits are redacted);
- a cubic diophantine in two unknowns $x, y$ with a known constant $a$ (300 bits) and a known right-hand side $b$.

The flag is masked: $c \equiv (x^2 + m + y)^e \pmod n$. Even with the full private key,
decrypting only gives $x^2 + m + y$ - we still need $x$ and $y$ themselves.

There are therefore two things to recover, and they look independent:

- **the factorisation of $n$**, from a quarter of $d$;
- **$x$ and $y$**, from the diophantine.

The whole trick of the challenge is that they are the *same* problem.

---

## 2. Half One: the diophantine is made of $n$

The equation is symmetric in $x$ and $y$, which invites the classical substitution

$$u = x + y, \qquad v = xy .$$

The three symmetric pieces expand as

$$x^3 + y^3 = u^3 - 3uv, \qquad xy(x+y) = uv, \qquad x^2 + y^2 = u^2 - 2v,$$

so the left-hand side collapses to

$$x^3 + y^3 + 4xy(x+y) - a(x^2+y^2) \;=\; u^3 - 3uv + 4uv - a(u^2 - 2v) \;=\; u^3 + uv - a(u^2 - 2v).$$

Setting that equal to $b$ and collecting the terms that carry $v$:

$$v\,(u + 2a) \;=\; -u^3 + a u^2 + b .$$

Now divide the right-hand side by $u + 2a$ as polynomials in $u$:

$$-u^3 + a u^2 + b \;=\; (u + 2a)\left(-u^2 + 3au - 6a^2\right) \;+\; \left(12a^3 + b\right),$$

which gives

$$v \;=\; -u^2 + 3au - 6a^2 \;+\; \frac{12a^3 + b}{u + 2a}.$$

Since $x, y$ are integers, $v$ is an integer, and therefore

$$\boxed{\,(u + 2a) \ \big|\ 12a^3 + b\,}$$

Compute $12a^3 + b$ from the published constants and the challenge gives itself away:

$$12a^3 + b \;=\; n .$$

That is the "aha". **One of the factors of $n$ is $u + 2a = x + y + 2a$.** Rearranging the
division above also tells us what the cofactor is:

$$n \;=\; (u + 2a)\,\bigl(v + u^2 - 3au + 6a^2\bigr), \qquad\text{i.e.}\qquad p = u + 2a,\quad q = v + u^2 - 3au + 6a^2 .$$

So the diophantine is solvable **iff** we can factor $n$ - and, conversely, once $n$ is
factored the diophantine is a two-line computation. Everything now rests on the leaked
bits of $d$.

---

## 3. Half Two: factoring $n$ from a quarter of $d$

This is **Theorem 9** of Boneh's *Twenty Years of Attacks on the RSA Cryptosystem*
(Boneh-Durfee-Frankel): given the low $\tfrac{1}{4}\log_2 n$ bits of $d$, an RSA modulus can
be factored in time polynomial in $e$. Here $n$ is 907 bits, so the theorem needs $227$
bits and we are given $240$ - a deliberately thin margin.

### 3.1 A quadratic congruence for $p$

By construction $ed \equiv 1 \pmod{\varphi(n)}$, so for some integer $k$ with $1 \le k < e$:

$$ed = 1 + k\,\varphi(n) = 1 + k\,(n - p - q + 1).$$

Multiply through by $p$ and substitute $pq = n$:

$$edp = p + k\,(np - p^2 - n + p) \;\Longrightarrow\; k\,p^2 + (ed - kn - k - 1)\,p + kn = 0 .$$

That identity holds over $\mathbb{Z}$, hence modulo anything - in particular modulo
$2^{240}$, where $ed$ can be evaluated from the leak alone:

$$f_k(t) \;=\; k\,t^2 + (e\,d_{\text{low}} - kn - k - 1)\,t + kn \;\equiv\; 0 \pmod{2^{240}} .$$

Because the derivation is symmetric in $p$ and $q$, **both** $p \bmod 2^{240}$ and
$q \bmod 2^{240}$ are roots of $f_k$ for the correct $k$ - and by Vieta their product is
$kn/k = n \bmod 2^{240}$, which gives a free consistency filter.

### 3.2 Solving it bit by bit

Roots modulo a power of two are found by lifting: $p$ is odd, so start from $t = 1$, and at
each step $i$ keep the extensions $t$ and $t + 2^i$ that still satisfy $f_k(t) \equiv 0 \pmod{2^{i+1}}$.

```python
def roots_mod_2L(k):
    A, B, C = k, e*d_low - k*n - k - 1, k*n
    f = lambda t: A*t*t + B*t + C
    cands = [1] if f(1) % 2 == 0 else []
    for i in range(1, L):
        m2, nxt = 1 << (i+1), []
        for t in cands:
            if f(t) % m2 == 0:          nxt.append(t)
            if f(t + (1<<i)) % m2 == 0: nxt.append(t + (1<<i))
        cands = nxt
        if not cands:
            break
    return cands
```

For a wrong $k$ the candidate tree usually dies within a few dozen bits; for the right one
it survives to the full 240 bits, leaving a handful of residues (4 here).

### 3.3 Coppersmith, and the part that is easy to get wrong

For each surviving residue $r$ we know $p \equiv r \pmod{2^{240}}$, i.e.

$$p = r + 2^{240} z_0, \qquad z_0 \ \text{small}.$$

Finding $z_0$ is Coppersmith's "factoring with known low bits": find a small root of the
monic $f(z) = z + r\cdot 2^{-240} \bmod n$ that reveals a factor $p \ge n^{\beta}$.

**The trap is $\beta$.** The instinct is $\beta = 1/2$ (balanced primes), and with that value
`small_roots` finds nothing. The equation itself tells you the split is *not* balanced.
If $x \sim y \sim M$, then

$$p = u + 2a \sim 2M + 2a \quad (\approx 2^{302}), \qquad q = v + u^2 - 3au + 6a^2 \sim M^2 + 4M^2 = 5M^2 \quad (\approx 2^{604}),$$

because $a$ is only 300 bits. So $n \approx 2^{907}$ splits roughly **one third / two thirds**:

$$\beta \;=\; \frac{\log_2 p}{\log_2 n} \;\approx\; \frac{303}{907} \;=\; 0.334 .$$

With $\beta = 0.33$ and $\varepsilon = 0.03$ the attack is comfortable: $p$ has $303 - 240 = 63$
unknown bits, while Coppersmith reaches $\log_2 n \cdot (\beta^2 - \varepsilon) \approx 71.6$ bits.

```python
F.<z> = PolynomialRing(Zmod(n))
def coppersmith(r):
    for root in (2**L * z + r).monic().small_roots(X=2**66, beta=0.33, epsilon=0.03):
        g = gcd(Integer(2**L*Integer(root) + r), n)
        if 1 < g < n:
            return g
```

Sweeping $k = 1, 2, \dots, e$ and calling this on every surviving residue finds

$$k = 225$$

and with it the factorisation.

---

## 4. Closing the loop: $u$, $v$, then $x$, $y$

$n = pq$ has exactly four divisors, so $u + 2a$ has four candidates. For each divisor $D$
set $u = D - 2a$ and recover $v$ from the division of Section 2:

$$v \;=\; \frac{-u^3 + au^2 + b}{u + 2a},$$

keeping only the candidate where $v$ is a positive integer and $u^2 - 4v$ is a perfect
square. Only $D = p$ survives. Then $x$ and $y$ are the roots of $t^2 - ut + v$:

$$x,\,y \;=\; \frac{u \pm \sqrt{u^2 - 4v}}{2}.$$

Finally, with $d = e^{-1} \bmod (p-1)(q-1)$,

$$m \;=\; c^{\,d} \bmod n \;-\; x^2 \;-\; y .$$

The equation is symmetric but the mask is not, so try both orientations
($\,\cdot - x^2 - y$ and $\,\cdot - y^2 - x$); here the wrong one goes negative and the
right one prints the flag.

---

## 5. Result

```text
k = 225
p = 10465031477451690022868162641470703272755037572259955627850368131633813899196545329405001801
q = 54499289044124479417325060512438429304368278371469718655249223374994092006845363946924518244114728291011217561355411529847020310089550631805511297896027855789125549774948704965117983
x = 3370402694687847312977553534082180980403919005694453508367892804233394902351444671669725443
y = 4389474842352415682012721443708276158776619687114891346568003469293054668636070216259373534

COMPFEST18{s3c0nd_c04t_0f_v4rn1sh_st1ll_cr4cks_wh3n_d_l34ks_1ts_l0w_b1ts}
```

`solver/solve.sage` performs the whole chain and finishes in **49 s on a single core**
(SageMath 10.7, Apple silicon):

```bash
sage solver/solve.sage
```

---

## 6. What changed from the original *Polish*

| | Polish (CryptoCTF 2021) | Varnish |
| :--- | :--- | :--- |
| Equation | $x^2(y-a) + y^2(x-a) = b$ | $x^3 + y^3 + 4xy(x+y) - a(x^2+y^2) = b$ |
| After $u = x+y,\ v = xy$ | $v(u + 2a) = au^2 + b$ | $v(u + 2a) = -u^3 + au^2 + b$ |
| Hidden identity | $4a^3 + b = n$ | $\mathbf{12a^3 + b = n}$ |
| First factor | $p = u + 2a$ | $p = u + 2a$ |
| Second factor | $q = v - au + 2a^2$ | $q = v + u^2 - 3au + 6a^2$ |
| Parity constraint | $a$ odd | $\mathbf{a}$ **even** (otherwise $q$ is always even - see below) |
| $n$ / leak | 773 bits / 221 bits of $d$ | 907 bits / 240 bits of $d$ |
| $e$ | 65537 (~20 cores) | 257 (~1 core-minute) |

The cubic term is what forces the rework: the numerator picks up a $-u^3$, so the long
division produces the quotient $-u^2 + 3au - 6a^2$ instead of $au - 2a^2$, the remainder
becomes $12a^3 + b$ instead of $4a^3 + b$, and the cofactor $q$ is now quadratic in $u$.
Copying the original's constants yields a number that is not $n$, and the challenge stalls
at step one.

---

## 7. Notes for organisers

**Parity.** With $a$ odd the challenge is impossible to generate: $p = u + 2a$ forces $u$
odd, $u$ odd forces $v = x(u-x)$ even, and then
$q \equiv v + u^2 - 3au + 6a^2 \equiv 0 + 1 + 1 \equiv 0 \pmod 2$ - always composite.
`genkey` therefore clears the low bit of $a$. This is specific to this cubic; the original
equation has the opposite constraint.

**Cost knob.** The sweep costs $O(e)$ lifts plus roughly $4e$ Coppersmith calls
(~0.05 s each). $e = 257$ keeps a full worst-case sweep near one minute, which suits a
timed final; $e = 65537$ would reproduce the original's ~3.6 CPU-hours (hence the 20 cores
in the CryptoCTF writeup) and is a drop-in change in `chall.py` if the round is longer.
The $k$ actually drawn here is 225 of 257, so the published instance is close to the
worst case rather than a lucky early hit.

**Leak margin.** 240 leaked bits against a $227$-bit requirement is deliberately tight:
enough for the theorem, not enough to make Coppersmith trivial (63 unknown bits of $p$).

**Regenerating.** Keep `secret.py` next to `chall.py` and run `python3 chall.py > output.txt`.
Ship **only** `public/` (`chall.py`, `output.txt`, `description.md`) - `secret.py` holds the flag.

**Solver dependency.** `solve.sage` needs SageMath for `small_roots`; the rest of the chain
is plain Python integer arithmetic.
