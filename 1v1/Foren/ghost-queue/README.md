# Ghost Queue

`Ghost Queue` is a 1v1 live Linux forensic challenge. The service exposes a small forensic console backed by a filter process that has an open descriptor for a deleted spool file.

## Release

- Author: PolarBear7
- Connection: `nc 34.1.203.129 7713`
- Public attachment: `public/ghost-queue.zip`
- Dist password: `GQ-7mP4xV2qL9sR`

The password is included here for committee distribution. The encrypted public ZIP contains one participant-facing `README.md` and the responder evidence only.

## Local QA

```bash
docker compose up
nc 127.0.0.1 7713
```

The public ZIP contains responder notes. The live console holds an actual open temporary-file descriptor. The document receipt changes on service restart; the final flag stays static. Recover and submit within the same service lifetime.

## Technical focus

Process state, `/proc`-style descriptor reasoning, deleted-file recovery, and incident evidence correlation. The setting is inspired by CUPS incidents including CVE-2024-47177, but no real vulnerability is shipped or exploited.
