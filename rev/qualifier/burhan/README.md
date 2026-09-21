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
