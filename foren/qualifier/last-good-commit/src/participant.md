# Last Good Commit

Author: PolarBear7

The inventory database disagrees with the warehouse record. Recover the committed shipment record that agrees with the independent evidence.

Connection: `nc 34.1.203.129 7749`

Use `help` for the exact proof encoding. The receipt is part of the recovered record. Submit the case flag to CTFd.

## Hints

1. Keep the database and WAL together; opening the latest state is only the beginning.
2. A WAL frame with a nonzero database-size field ends a transaction. Reconstruct the state at each commit boundary on copies.
3. Match the warehouse record, then include that version's receipt, as lowercase hex, in the proof.
