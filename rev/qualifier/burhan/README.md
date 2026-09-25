# Burhan
by demtcsre

---

## Flag
```
COMPFEST18{burhan_come_back}
```

## Zip Password
```
cf18-burhan
```

## Description
Burhan, burung hantu itu, sudah lama dipelihara anak-anak lab. Dia tidak
bisa bicara. Sodorkan kunci, dia cuma mengangguk atau menggeleng, dan tidak
pernah repot menjelaskan kenapa.

File-only challenge. No connection info.

## Difficulty
medium

## Tags
rev, android, feistel, crypto

## Hints
- **Initial:**
  ```
  Yang disimpen bukan kuncinya, hasil olahannya. Bisa diputer balik.
  ```
- **10th minute:**
  ```
  jadx -d out app-release.apk. Cari method yang manggil enkripsi 4x.
  ```
- **15th minute:**
  ```
  for k in reversed(K): L,R = R^F(L,k), L.
  ```

## Deployment
- How to compile (CWD is /src):
```
gradle :app:assembleRelease
```
- How to run:
```
adb install -r app-release.apk
```

The shipped `src/app-release.apk` was not produced by Gradle. It was built
directly from the same sources with SDK build-tools 34.0.0:
```
aapt2 compile --dir app/src/main/res -o res.zip
aapt2 link -o base.apk -I android.jar --manifest app/src/main/AndroidManifest.xml \
      --java gen --min-sdk-version 24 --target-sdk-version 34 res.zip
javac -source 11 -target 11 -cp android.jar -d classes app/src/main/java/id/compfest/burhan/*.java gen/.../R.java
d8 --min-api 24 --lib android.jar --output dex classes/**/*.class
zipalign -f -p 4 unsigned.apk aligned.apk
apksigner sign --ks debug.keystore --out app-release.apk aligned.apk
```

## Verification
No obfuscation config is present. `app/build.gradle` sets:
```
minifyEnabled false
shrinkResources false
```
There is no `proguard-rules.pro`, no `proguardFiles` line, no dProtect, and no
`-keep` rules anywhere in the project:
```
$ grep -rniE 'minify|shrink|proguard|r8|dprotect|obfusc' src/
src/app/build.gradle:            minifyEnabled false
src/app/build.gradle:            shrinkResources false
```

Readability was verified with jadx 1.5.1:
```
$ jadx -d out app-release.apk
INFO  - loading ...
INFO  - processing ...
INFO  - done
```
Full transcript, including the decompiled class, is in
`writeup/jadx-transcript.txt`. The decompiled `Feistel` keeps real method names
(`f`, `pack`, `encryptBlock`, `check`), the literal `T` / `K` / `CT` arrays and
the 4-round loop. Only local variable names are lost, which is normal for dex.

Friction audit of the shipped APK, re-run against `src/app-release.apk`:
```
$ jadx -d out app-release.apk && find out/sources -name '*.java'
out/sources/id/compfest/burhan/Feistel.java
out/sources/id/compfest/burhan/MainActivity.java
out/sources/id/compfest/burhan/R.java

$ grep -inE 'thread|handler|post\(|runnable|async|executor|looper' out/sources/id/compfest/burhan/*.java
(no matches)
```
Three classes total, one Activity, no anonymous inner classes. `onClick` calls
`Feistel.check` inline with no indirection. `R.java` is 24 lines of resource ids.
Nothing to trim.

## Notes
- SHA256 of both distributed artifacts:
  ```
  app-release.apk  693934e39f4301bc3e10fb5af2d102839cdbf1b5babccf1238e4873fed5220ad
  dist-burhan.zip  690026a32b7558141d15057cc218ee2cd624482070dee6852bf77fccf248451e
  ```
