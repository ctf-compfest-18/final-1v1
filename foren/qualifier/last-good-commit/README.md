# Last Good Commit

`Last Good Commit` is a 1v1 database-forensics challenge about recovering a trustworthy state from SQLite artifacts.

## Release

- Author: Kyraux
- Connection: `nc 34.1.203.129 7749`
- Public attachment: `public/last-good-commit.zip`
- Dist password: `LGC-4nZ8pQ6vK2dM`

The password is included here for committee distribution. The participant README (`public/README.md`: name, author, description, connection, hint 1) is published both next to and inside the password-protected evidence ZIP `public/last-good-commit.zip`. Hints 2 and 3 are released by the organizer over time (see below) and are not shipped in the ZIP.

## Hints (give via Discord; keep out of the ZIP)

Hint 1 ships in the participant README. Give hint 2 at the 10-minute mark and hint 3 at the 15-minute mark (desperate) via Discord.

1. Released: "Keep the database and WAL together; opening the latest state is only the beginning."
2. 10 minutes: "The database already shows the overwritten row. The trustworthy version is an earlier transaction that still lives in the write-ahead log."
3. 15 minutes (desperate): "A WAL frame with a nonzero 'database size after commit' field ends a transaction. Copy `inventory.db` and `inventory.db-wal`, truncate the WAL after the first commit frame, open the copy with sqlite3, read the original row (`SHIP-8821`, `BG-14`, quantity `6`, approved `1`, plus its receipt), then submit the SHA-256 of `shipment=SHIP-8821|sku=BG-14|quantity=6|approved=1|receipt=<lowercase hex>` with no trailing newline."

## Local QA

```bash
docker compose up
nc 127.0.0.1 7749
```

The public ZIP contains a real SQLite database and WAL. The console documents the proof format and validates the recovered record, including its receipt. It does not return the evidence or decoded WAL. Build with the staging release.py script, which updates src/answer.json and the encrypted ZIP together.

## Technical focus

SQLite page/WAL inspection, commit-state reasoning, timeline correlation, and validation against an independent warehouse record. The SQLite file-format behavior is the reference material; no CVE is required.
