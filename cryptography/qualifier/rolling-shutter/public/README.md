# Rolling Shutter

by fele

---

## Description
London Bridge is falling down,
Falling down, falling down.
London Bridge is falling down,
My fair lady.

## Hints
* Use the highly predictable PNG file signature to recover the first few consecutive internal states of the keystream.
* Set up the recurrence equations for the known states and subtract them to eliminate the unknown increment.