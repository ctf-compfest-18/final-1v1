# Write Up RSA-Child

## Encryption

1. Read the flag and convert it to a big-endian integer m.
2. Generate the related primes p and q as above.
3. Set n = p*q and e = 65537.
4. Encrypt c = m^e mod n.
5. Publish n, e and c alongside the source code.

## Intended solution, step by step

### 1. Recognize the relation

Write q = 7*p + delta, where delta includes both 2*offset and the small
increment used to reach a prime. delta is around 2^520 to 2^521, which is
tiny compared with p. However, q-p is around 6*p, so ordinary Fermat on n
is infeasible: its intended factor pair is far apart.

### 2. Change the number being factored

Multiply the public modulus by seven:

    N = 7*n = (7*p)*q

Now its factors 7*p and q are close. Fermat's identity applies to odd
factors; they do not both have to be prime.

### 3. Use the difference of squares

Set A = (7*p+q)/2 and B = (q-7*p)/2. Then:

    N = A^2 - B^2
    N = (A-B)*(A+B)

Starting at a = ceil(sqrt(N)), increment a until a*a-N is a perfect square.
Use math.isqrt, not floating-point square roots.

For this generated relation, the nearby factor pair is:

    a-b = 7*p
    a+b = q

### 4. Recover the original factors

Do not treat both factors of 7*n as RSA primes. Remove the multiplier:

    p = gcd(a-b, n)
    q = n // p

The GCD also works if the two recovered factors are swapped.

### 5. Decrypt

    phi = (p-1)*(q-1)
    d = pow(e, -1, phi)
    m = pow(c, d, n)

Convert m to big-endian bytes. The result is the flag.

## Why the search is fast

Exactly:

    A - sqrt(N) = B^2 / (A + sqrt(N))

Here B is roughly the 520-bit offset, and A is approximately 7*p. Ignoring
the negligible prime-search increment, the number of increments is about
offset^2/(14*p): roughly 1,170 to 9,363 for the configured ranges. This is
fast on an ordinary computer. The thinking and adapting the attack are the
intended difficulty, rather than making competitors wait for computation.

## Small worked example

Take p=101 and q=727=7*101+20. Then n=73427 and N=7*n=513989.
Start a=717. We have a^2-N=514089-513989=100=10^2.
The recovered factors are 707 and 727. gcd(707,73427)=101 gives p.

## Optional hints

At around three minutes, if needed: "Which two quantities in get_primes()
are actually close together?"

A stronger hint: "Fermat factorization need not start from n itself."

Final hint: "Factor 7*n as a difference of squares, then take a GCD with n."

## Flag

COMPFEST18{4_ch4ng3_0f_sc4l3_br1ngs_th3_pr1m3s_b4ck_t0g3th3r_h3h3h3_c0ngr4atZzz}

## Organizer notes

This is a static source-review puzzle, so specialized RSA tools may solve it
quickly. Do not rely on obfuscation to guarantee a five-minute solve.
Do not raise the offset length casually: each extra bit roughly quadruples
the Fermat iteration count. Playtest with a representative player before
assigning points or promising a fixed solve time.
