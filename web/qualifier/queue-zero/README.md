# Queue Zero

`Queue Zero` is a 1v1 web challenge built around a deterministic TOCTOU race on a single-use claim receipt. The redemption path checks `claim.redeemed` before an asynchronous delay and never re-checks it afterwards.

## Release

- Author: Kyraux
- Connection: http://34.1.203.129:4013
- Public attachment: `public/queue-zero.zip`
- Dist password: `QZ-nfuiHZKMeUY9`

The password is included here for committee distribution. The encrypted public ZIP contains one participant-facing `README.md` only. No source code is shipped to participants.

## Local QA

```bash
docker compose up --build
curl http://127.0.0.1:4013/health
```

The service uses only the Node.js standard library and has no npm dependencies. The static flag is injected through the `FLAG` environment variable.

## Hints (give via Discord; keep out of the ZIP)

Hint 1 ships in the participant README. Give hint 2 at the 10-minute mark and hint 3 at the 15-minute mark (desperate) via Discord.

1. Released: "Look closely at what happens between the check and the state update."
2. 10 minutes: "The receipt is checked before an asynchronous delay and only marked settled afterwards, so concurrent redemptions can all pass the check."
3. 15 minutes (desperate): "Open one claim (`POST /api/claims/start`), then redeem all three lanes (`north`, `east`, `west`) in parallel with the same token so each passes the pre-delay check. Collect the three distinct fragments, `POST /api/claims/assemble`, then `GET /api/releases/<handoff>` for the label."

## Intended solve

Open one claim, then redeem all three settlement lanes in parallel with the same receipt. Every request passes the pre-delay check, so all three lane fragments are issued. Assemble the three distinct fragments to obtain the release handoff and redeem it for the label.

## Technical focus

Asynchronous state-change ordering, single-use token races, and per-process HMAC binding of lane fragments. This is a local TOCTOU simulation and is not tied to a specific CVE.
