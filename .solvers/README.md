# Organizer Solvers

Organizer-only. Do not include this directory in participant releases.

`solve.py` solves all three Finals web challenges against a local or remote deployment. Standard library only, no dependencies.

```bash
python solve.py                        # all challenges on 127.0.0.1
python solve.py --host 34.1.203.129    # remote deployment
python solve.py --only snow --snow 4021
```

Covered:

| Key | Challenge | Default port | Path |
| --- | --- | ---: | --- |
| `aurora` | Aurora Manifest Exchange | 4007 | duplicate-key JSON parser differential |
| `queue` | Queue Zero | 4013 | parallel redeem TOCTOU race |
| `snow` | Snowblind Relay | 4021 | weak HS256 secret recovered from the `robots.txt` wordlist |

Isolation notes:

- Participant distribution is only `web/*/*/public/<challenge>.zip`, which contains a single `README.md`.
- Each challenge `.dockerignore` excludes `public/` and `writeups/`, and the Docker build context is the challenge folder, so this directory never enters any service image.
- This directory is a hidden dot-folder at the repository root and is not referenced by any `challenge.yml`.
