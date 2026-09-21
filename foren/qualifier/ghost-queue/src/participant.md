# Ghost Queue

Author: PolarBear7

A print job disappeared from the queue during incident cleanup. Investigate the remaining process evidence and recover the document.

Connection: `nc 34.1.203.129 7713`

Use `help` for the console commands and proof encoding. The recovered case flag is submitted to CTFd.

## Hints

1. A removed directory entry does not necessarily remove an open file.
2. Correlate the job in the collection log with the process and its descriptors.
3. Hash the exact recovered bytes, including their final newline.
