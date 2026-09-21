# Burhan — REV 3, APK Feistel

**Category:** Reverse Engineering · **Difficulty:** medium
**Flag:** `COMPFEST18{burhan_come_back}`

---

## 1. What you get

One APK. Install it and you get a text field, a button, and an owl that either
nods or shakes its head. No network, no permissions, no native library.

```
$ unzip -P cf18-burhan burhan.zip
$ jadx -d out app-release.apk
INFO  - loading ...
INFO  - processing ...
INFO  - done

$ ls out/sources/id/compfest/burhan/
Feistel.java  MainActivity.java  R.java
```

Nothing is obfuscated. `Feistel.java` comes back with its method names intact
(`f`, `pack`, `encryptBlock`, `check`) and all three constant arrays inline.
Only local variable names are gone, which is just what dex does.

## 2. The check

```java
public static boolean check(String str) {
    if (str.length() != 28 || !str.startsWith("COMPFEST18{") || str.charAt(27) != '}') {
        return false;
    }
    byte[] bytes = str.substring(11, 27).getBytes(StandardCharsets.US_ASCII);
    int i = 0;
    for (int i2 = 0; i2 < 16; i2 += 8) {
        int[] encryptBlock = encryptBlock(pack(bytes, i2), pack(bytes, i2 + 4));
        int[] iArr = CT;
        if (encryptBlock[0] != iArr[i] || encryptBlock[1] != iArr[i + 1]) {
            return false;
        }
        i += 2;
    }
    return true;
}
```

16 body bytes, two 64-bit blocks, each encrypted and compared against a stored
constant. The app only ever encrypts. It never decrypts anything, so the flag
is not sitting in the APK in any form `strings` will find.

## 3. Endianness

This is the detail that silently ruins an otherwise correct solve, so pin it
down before writing any code:

```java
private static int pack(byte[] bArr, int i) {
    return (bArr[i + 3] & 255) | ((bArr[i] & 255) << 24)
         | ((bArr[i + 1] & 255) << 16) | ((bArr[i + 2] & 255) << 8);
}
```

jadx reorders the terms, but the shifts give it away: **`b[i]` is shifted left
by 24, so it is the most significant byte. The packing is big-endian.**

So for block 0, `L = body[0..3]` and `R = body[4..7]`, each read big-endian.
Unpacking at the end has to match: `l.to_bytes(4, "big") + r.to_bytes(4, "big")`.
Get it backwards and you recover a byte-swapped string that looks like garbage
but is exactly 16 characters long, which is a convincing way to lose five
minutes.

## 4. The round function, and why it is never inverted

```java
private static final int[] T = { 1518673737, 1137498011, ... };   // 256 entries
private static final int[] K = { -983495488, -1911790962, -1565544969, -220540650 };
private static final int[] CT = { -2071679150, 38547500, 808035184, -1163625378 };

private static int f(int i, int i2) {
    int i3 = i ^ i2;
    int[] iArr = T;
    return iArr[(i3 >>> 24) & 255] ^ iArr[i3 & 255] ^ iArr[(i3 >>> 8) & 255] ^ iArr[(i3 >>> 16) & 255];
}
```

`F` is not invertible, deliberately. The 256-entry table holds only 137 distinct
values, so 119 entries are duplicates and some values appear five times. On top
of that, `F` xors four table lookups down into one 32-bit result, folding the
input through a many-to-one map. Given an output of `F` you cannot recover its
input, and no amount of staring at the table changes that.

It does not matter. A Feistel network is invertible **whatever `F` does**:

```java
private static int[] encryptBlock(int l, int r) {
    for (int round = 0; round < 4; round++) {
        int t = r;
        r = l ^ f(r, K[round]);
        l = t;
    }
    return new int[] { l, r };
}
```

One round maps `(L, R)` to `(L', R') = (R, L ^ F(R, k))`. Read that backwards:

```
R = L'                          the old right half is just the new left half
L = R' ^ F(R, k) = R' ^ F(L', k)
```

`F` appears on the right-hand side only. You **evaluate** it, forwards, on a
value you already have. You never solve `F(x) = y` for `x`. That is the whole
trick, and it is why a lossy round function is a safe thing to put inside a
Feistel cipher.

Decryption is therefore the same loop with the halves swapped and the keys
consumed in reverse:

```python
def decrypt_block(l, r):
    for rnd in range(3, -1, -1):
        t = l
        l = (r ^ f(l, K[rnd])) & 0xFFFFFFFF
        r = t
    return l, r
```

Four rounds, four round keys, in the order `K[3], K[2], K[1], K[0]`.

## 5. Solve

Pull `T`, `K` and `CT` straight out of the decompiled source, run both
ciphertext blocks backwards, concatenate, wrap. See `solve.py`.

```
$ python3 solve.py
COMPFEST18{burhan_come_back}
re-encrypt matches CT: ['0x8484af52', '0x24c302c', '0x3029a370', '0xbaa47c5e']
table collisions: 119 of 256 entries -> F is many-to-one
```

The solver re-encrypts its own answer and asserts it lands back on the stored
`CT`, so a wrong endianness or an off-by-one in the key order fails loudly
instead of printing a plausible wrong flag.

## 6. Why brute force is not an option

The body is 16 bytes. Even restricted to printable ASCII that is `95^16`, about
`2^105`. The app gives one bit of feedback per guess and compares both blocks
before answering, so there is no per-block or per-byte oracle to grind. Running
the cipher backwards takes microseconds. Guessing takes longer than the universe
has been around.

## 7. Layout

```
./
  challenge.yml      CTFd metadata
  README.md          author-facing
public/
  burhan.zip         password-protected player distribution (apk + player README)
src/                 Android project root (Java)
  build.gradle  settings.gradle  gradle.properties
  app/build.gradle
  app/src/main/AndroidManifest.xml
  app/src/main/java/id/compfest/burhan/{Feistel,MainActivity}.java
  app/src/main/res/layout/activity_main.xml
  app/src/main/res/values/strings.xml
  app-release.apk    build output
  README.player.md   the README that goes inside the zip
writeup/
  solve.py  README.md  jadx-transcript.txt  jadx-Feistel.java
```
