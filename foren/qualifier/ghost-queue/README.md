# Ghost Queue

`Ghost Queue` is a 1v1 live Linux forensic challenge. The service exposes a small forensic console backed by a filter process that has an open descriptor for a deleted spool file.

## Release

- Author: PolarBear7
- Connection: `nc 34.1.203.129 7713`
- Public attachment: `public/ghost-queue.zip`
- Dist password: `GQ-7mP4xV2qL9sR`

The password is included here for committee distribution. The public dist is `public/README.md` (participant README: name, author, description, connection, hint 1) next to the password-protected evidence ZIP `public/ghost-queue.zip`. Only one hint is released.

## Internal hints (not released)

Only hint 1 is published. Hints 2 and 3 are kept here for organizers and the official writeup:

2. Correlate the job in the collection log with the process and its descriptors.
3. Hash the exact recovered bytes, including their final newline.

## Local QA

```bash
docker compose up
nc 127.0.0.1 7713
```

The public ZIP contains responder notes. The live console holds an actual open temporary-file descriptor. The document receipt changes on service restart; the final flag stays static. Recover and submit within the same service lifetime.

## Technical focus

Process state, `/proc`-style descriptor reasoning, deleted-file recovery, and incident evidence correlation. The setting is inspired by CUPS incidents including CVE-2024-47177, but no real vulnerability is shipped or exploited.
