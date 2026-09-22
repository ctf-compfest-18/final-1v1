# No Time to Prime

by racoonhunter

## Description

Three recovery tokens are missing from the vault. Recover them from the diagnostic dumps and unlock the final flag.

## Usage

From this directory, use SageMath with PyCryptodome:

```sh
sage -python -m pip install pycryptodome
sage -python probset/tests/verify.py
sage -python probset/solver/solve_all.py
```

Generate a new instance and rebuild the ZIP:

```sh
sage -python probset/generator/generate.py --force
sage -python package.py
```

The flag is in `probset/secrets/flag.txt`. Run the console with
`python participant/run.py`. The solution is in
[../writeup/README.md](../writeup/README.md), with data encoding in
[../writeup/FORMAT.md](../writeup/FORMAT.md).
