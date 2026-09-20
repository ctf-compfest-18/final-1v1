# Last Good Commit

`Last Good Commit` is a 1v1 database-forensics challenge about recovering a trustworthy state from SQLite artifacts.

## Release

- Author: PolarBear7
- Connection: `nc 34.1.203.129 7749`
- Public attachment: `public/last-good-commit.zip`
- Dist password: `LGC-4nZ8pQ6vK2dM`

The password is included here for committee distribution. The encrypted public ZIP contains one participant-facing `README.md` and the database evidence only.

## Local QA

```bash
docker compose up
nc 127.0.0.1 7749
```

The public ZIP contains a real SQLite database and WAL. The console documents the proof format and validates the recovered record, including its receipt. It does not return the evidence or decoded WAL. Build with the staging release.py script, which updates src/answer.json and the encrypted ZIP together.

## Technical focus

SQLite page/WAL inspection, commit-state reasoning, timeline correlation, and validation against an independent warehouse record. The SQLite file-format behavior is the reference material; no CVE is required.
