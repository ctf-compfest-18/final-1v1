# Relay Receipt

by racoonhunter

## Description

Two directories, one delivery, two receipts. The issuer thought they were separate enough. Can you open the vault?

## Usage

From this directory, use Python 3.10 or later:

```sh
python3 -m pip install -r requirements.txt
python3 probset/verify.py
python3 probset/solve.py participant
```

Generate a new instance and rebuild the ZIP:

```sh
python3 probset/regenerate.py
python3 package.py
```

The flag is in `probset/flag.txt`. The solution is in
[../writeup/README.md](../writeup/README.md).
