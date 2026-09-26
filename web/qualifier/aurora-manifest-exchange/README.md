# Aurora Manifest Exchange

`Aurora Manifest Exchange` is a 1v1 web challenge built around a JSON parser differential: the validation stage reads the first occurrence of every flat key, while the release worker re-parses the stored body with `JSON.parse`, which keeps the last occurrence of a duplicate key.

## Release

- Author: Kyraux
- Connection: http://34.1.203.129:4007
- Public attachment: `public/aurora-manifest-exchange.zip`
- Dist password: `AME-Ts9I6isU7nu2`

The password is included here for committee distribution. The encrypted public ZIP contains one participant-facing `README.md` only. No source code is shipped to participants.

## Local QA

```bash
docker compose up --build
curl http://127.0.0.1:4007/health
```

The service uses only the Node.js standard library and has no npm dependencies. The static flag is injected through the `FLAG` environment variable.

## Hints (give via Discord; keep out of the ZIP)

Hint 1 ships in the participant README. Give hint 2 at the 10-minute mark and hint 3 at the 15-minute mark (desperate) via Discord.

1. Released: "The same manifest can be interpreted more than once before release."
2. 10 minutes: "The preview validator and the release worker do not parse a manifest the same way: one keeps the first occurrence of a repeated field, the other keeps the last."
3. 15 minutes (desperate): "`POST /api/manifests/preview` with a JSON body containing duplicate `scope`/`artifact` keys, the first pair `partner`/`dispatch-note` and a trailing pair `control-room`/`sealed-export`. Then `POST /api/manifests/commit` with the returned `approvalId`, poll `GET /api/jobs/<jobId>` until `state` is `ready`, and `GET /api/exports/<handoff>` for the label."

## Intended solve

Submit a manifest whose first `scope`/`artifact` pair is `partner`/`dispatch-note` and whose duplicate trailing pair is `control-room`/`sealed-export`. The validator approves it, the release worker exercises the control-room branch, and the polling job hands back a one-shot export token that yields the label.

## Technical focus

Duplicate-key JSON interpretation, validate-versus-use mismatch, and short-lived asynchronous handoff. The concept is inspired by CVE-2017-12635 (CouchDB duplicate-key authorization mismatch); no vulnerable dependency is shipped or exploited.
