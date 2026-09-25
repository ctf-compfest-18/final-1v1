# Ghost Queue

`Ghost Queue` is a 1v1 live Linux forensic challenge. The service exposes a small forensic console backed by a filter process that has an open descriptor for a deleted spool file.

## Release

- Author: Kyraux
- Connection: `nc 34.1.203.129 7713`
- Public attachment: `public/ghost-queue.zip`
- Dist password: `GQ-7mP4xV2qL9sR`

The password is included here for committee distribution. The participant README (`public/README.md`: name, author, description, connection, hint 1) is published both next to and inside the password-protected evidence ZIP `public/ghost-queue.zip`. Hints 2 and 3 are released by the organizer over time (see below) and are not shipped in the ZIP.

## Hints (give via Discord; keep out of the ZIP)

Hint 1 ships in the participant README. Give hint 2 at the 10-minute mark and hint 3 at the 15-minute mark (desperate) via Discord.

1. Released: "A removed directory entry does not necessarily remove an open file."
2. 10 minutes: "The filter process still holds an open file descriptor for the deleted spool. Use the console's `lsof` to read the deleted spool id, then `read-spool <id>`."
3. 15 minutes (desperate): "On the console run `lsof` to get `/tmp/print-spool-<id> (deleted)`, then `read-spool <id>` to print the document, then submit the lowercase SHA-256 of those exact bytes including the final newline with `submit <sha256>`."

## Local QA

```bash
docker compose up
nc 127.0.0.1 7713
```

The public ZIP contains responder notes. The live console holds an actual open temporary-file descriptor. The document receipt changes on service restart; the final flag stays static. Recover and submit within the same service lifetime.

## Technical focus

Process state, `/proc`-style descriptor reasoning, deleted-file recovery, and incident evidence correlation. The setting is inspired by CUPS incidents including CVE-2024-47177, but no real vulnerability is shipped or exploited.
