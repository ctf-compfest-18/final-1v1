#!/usr/bin/env python3
"""Recover the flag from three tokens."""
import argparse
import getpass
from pathlib import Path
from app.crypto_core import MODULES, recover_final

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--challenge", type=Path, default=Path(__file__).parent / "challenge")
    args = parser.parse_args()
    tokens = {m: getpass.getpass(m + " token: ").strip() for m in MODULES}
    try:
        key, flag = recover_final(args.challenge, tokens)
    except (ValueError, KeyError, OSError) as exc:
        parser.exit(1, f"Recovery gagal: {exc}\n")
    print("Master key:", key.hex())
    print("Flag:", flag)

if __name__ == "__main__":
    main()
