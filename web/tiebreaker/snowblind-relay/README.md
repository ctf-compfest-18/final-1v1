# Snowblind Relay

`Snowblind Relay` is a tiebreaker web challenge built around a weak HS256 JWT signing secret. The public session exposes a valid signature, and the leaked recovery wordlist referenced by `robots.txt` contains the signing secret.

## Release

- Author: Kyraux
- Connection: http://34.1.203.129:4021
- Public attachment: none; this is a live service only.
- Dist password: QXoSD15OXjumj9k8

This tiebreaker ships no participant hint. One reserve hint is documented below for organizers and is given via Discord only if both teams are stuck.

## Hint (reserve; give via Discord only if both teams are stuck)

"The session token is an HS256 JWT signed with a weak secret. `robots.txt` points to `/assets/relay-terms.txt`, a wordlist that contains the signing secret; recover it, then forge a token with `role: reviewer`, `aud: incident-relay`, `channel: snowblind`, request the reviewer handoff, and redeem it for the label."

## Local QA

```bash
docker compose up --build
curl http://127.0.0.1:4021/health
```

The service uses only the Node.js standard library and has no npm dependencies. `JWT_SECRET` defaults to the wordlist secret; production supplies the same value through the environment.

## Intended solve

Fetch `/api/session`, discover `/assets/relay-terms.txt` through `robots.txt`, match the candidate that reproduces the session signature, then forge a token with `role: reviewer`, `aud: incident-relay`, and `channel: snowblind`. Request the reviewer handoff and redeem it for the label.

## Technical focus

JWT signature verification, offline recovery of a weak HMAC secret from a supplied wordlist, and role/audience claim forgery. Inspired by CVE-2023-53951; no vulnerable JWT library is shipped.
