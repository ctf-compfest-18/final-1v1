password: `8CjCHRFG2aqSWt00`
### Hint 2 (10 Mins)
> Treat $6x^2 + 5xy + y^2$ as a quadratic in $y$. What is its discriminant? If it factors over $\mathbb{Z}$, can you absorb the linear terms $Ax + By$ into the same product?
### Hint 3 (15 Mins)
> The equation factors completely:
>
> $$(3x + y + \alpha)(2x + y + \beta) = b + \alpha\beta$$
>
> where $\alpha = 3B - A$ and $\beta = A - 2B$.
>
> Compute $b + \alpha\beta$. You'll find it equals $n$.
>
> So factoring $n$ (Fermat — the primes are close) gives you $p$ and $q$, which gives you $x$ and $y$ via a linear system: $x = (P - \alpha) - (Q - \beta)$, $y = 3(Q - \beta) - 2(P - \alpha)$. Try both $(P,Q)=(p,q)$ and $(q,p)$. Then decrypt: $m = c^d \bmod n - x^2 - y$.
