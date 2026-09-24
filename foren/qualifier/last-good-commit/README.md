# Last Good Commit

`Last Good Commit` is a 1v1 database-forensics challenge about recovering a trustworthy state from SQLite artifacts.

## Release

- Author: Kyraux
- Connection: `nc 34.1.203.129 7749`
- Public attachment: `public/last-good-commit.zip`
- Dist password: `LGC-4nZ8pQ6vK2dM`

The password is included here for committee distribution. The participant README (`public/README.md`: name, author, description, connection, hint 1) is published both next to and inside the password-protected evidence ZIP `public/last-good-commit.zip`. Only one hint is released.

## Internal hints (not released)

Only hint 1 is published. Hints 2 and 3 are kept here for organizers and the official writeup:

2. A WAL frame with a nonzero database-size field ends a transaction. Reconstruct the state at each commit boundary on copies.
3. Match the warehouse record, then include that version's receipt, as lowercase hex, in the proof.

## Local QA

```bash
docker compose up
nc 127.0.0.1 7749
```

The public ZIP contains a real SQLite database and WAL. The console documents the proof format and validates the recovered record, including its receipt. It does not return the evidence or decoded WAL. Build with the staging release.py script, which updates src/answer.json and the encrypted ZIP together.

## Technical focus

SQLite page/WAL inspection, commit-state reasoning, timeline correlation, and validation against an independent warehouse record. The SQLite file-format behavior is the reference material; no CVE is required.
