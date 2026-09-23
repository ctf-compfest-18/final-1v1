# Varnish (COMPFEST 18 - Final Round, Cryptography)

A re-cut of **Polish** (CryptoCTF 2021) with a different cubic diophantine, so the hidden
identity, the cofactor's shape, and the long division all have to be re-derived. Teams that
recall the original still have to redo the algebra: the constant is `12a^3 + b`, not `4a^3 + b`.

| | |
| :--- | :--- |
| **Flag** | `COMPFEST18{s3c0nd_c04t_0f_v4rn1sh_st1ll_cr4cks_wh3n_d_l34ks_1ts_l0w_b1ts}` |
| **Difficulty** | Hard |
| **Intended solve** | ~50 s of compute on one core, on top of the algebra |
| **Solver needs** | SageMath (`small_roots`) + pycryptodome |

## Layout

```
varnish/
├── public/                 <-- ship exactly this
│   ├── chall.py
│   ├── output.txt
│   └── description.md
├── challenge/              <-- authoring copy
│   ├── chall.py
│   ├── output.txt
│   ├── description.md
│   └── secret.py           <-- HOLDS THE FLAG, never ship
├── solver/solve.sage       <-- official solver, end to end
└── writeup.md
```

## Run

```bash
sage solver/solve.sage
```

## Regenerate a fresh instance

```bash
cd challenge && python3 chall.py > output.txt && cp chall.py output.txt description.md ../public/
```

Then re-run the solver against the new `output.txt` to confirm the instance is solvable
(the drawn `k` is random in `[1, e)`, so solve time varies up to ~1 minute).

## Two knobs

- **`e = 257`** - the sweep costs `O(e)` root-liftings plus roughly `4e` Coppersmith calls.
  257 keeps a worst-case sweep near a minute. Set `e = 65537` for the original's difficulty
  (~3.6 CPU-hours single core; the CryptoCTF team used 20 cores).
- **`leak = 240`** - the Boneh-Durfee-Frankel bound for a 907-bit modulus is 227 bits, so
  this is a thin 13-bit margin on purpose. Lowering it below 227 breaks the challenge.

`a` is forced **even** in `genkey`: with `a` odd this particular cubic makes `q` even for
every choice of `x`, and generation never terminates. See `writeup.md` §7.
