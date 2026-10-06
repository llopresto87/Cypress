---
name: local-android-demo-build
description: Build a reproducible, debug-signed demo APK of a Flutter app on a workstation or in a container, with the toolchain isolated under the project, build-time configuration passed explicitly, and the artifact verified before anyone calls it a release. Invoke when a demo or test APK is needed and no release keystore is available.
id: skill.local-android-demo-build
tier: 2
kind: skill
title: local-android-demo-build, a debug-signed demo APK built reproducibly and verified as what it is
owns:
  - local-android-demo-build.procedure
  - local-android-demo-build.verification
requires:
load_when:
  - "build a demo apk of the flutter app locally"
  - "debug-signed apk for a tester, no release keystore"
  - "build the android app in a container without a host toolchain"
stack:
  - library-corpus/language/flutter
est_tokens: 2100
---

# Suggested skill: local-android-demo-build

> Optional procedure, **stack-keyed** on Flutter: produce an Android APK for a
> demo or a tester, reproducibly, from a project that has no release signing
> set up. The output is **debug-signed** and labelled DEMO: it installs on a
> device that allows unknown sources, and it is never a store release.
> **Composes** `library-corpus/language/flutter.md` (Android build, its
> pitfalls and the toolchain compatibility chain; this page restates none of
> it), `core/method/secrets-posture.md` (what may be compiled into an app)
> and `protocols/verify.md` (verify the artifact, and record a gate not run)
> by reference. It adds the isolation layout, the scratch-copy rule for
> signing, the verification set and the container variant.

**Instantiate by supplying:** `<APP>` (the Flutter app directory), `<TOOLS>`
(a project-local, git-ignored directory for the SDK, caches and the scratch
copy), `<CHANNEL_VERSION>` (the Flutter release the app builds with),
`<JDK_HOME>` (a JDK the app's Gradle and plugins accept), `<ANDROID_SDK>`
(the Android SDK location), `<DEFINES>` (the build-time values the app reads
through `String.fromEnvironment`, if any) and `<DIST>` (where the APK is
published).

## When to apply

- A demo build is needed for a person or a device, and the project has no
  release keystore, or the keystore must not leave its owner.
- A build must be reproducible on another machine, or with no host toolchain
  at all.
- Not for a store release: that needs the release signing set-up the library
  page describes (`library-corpus/language/flutter.md`, Android build).

## 1. Isolate the toolchain under the project

*Replaces: building with whatever Flutter, JDK and caches the workstation
already has.*

- Download the Flutter SDK archive for `<CHANNEL_VERSION>` into `<TOOLS>` and
  check it against the SHA-256 that Flutter's official release manifest for
  the operating system lists for that archive. An archive that does not match
  is discarded, not retried until it passes.
- Point the caches inside the project for every build command:
  `GRADLE_USER_HOME=<TOOLS>/cache/gradle` and `PUB_CACHE=<TOOLS>/cache/pub`.
  Keep `<TOOLS>` out of version control; the caches grow to several gigabytes.
- **Know what still lands outside the project** and write it down with the
  build: `flutter config --jdk-dir <JDK_HOME>` writes a user-global Flutter
  setting, and Gradle installs the NDK and CMake into the shared Android SDK
  on the first build. Android documents this for Android Gradle Plugin 4.2.0
  and later, on one condition: the SDK licences were accepted in advance
  (`yes | <ANDROID_SDK>/cmdline-tools/latest/bin/sdkmanager --licenses`). An
  unattended or container build without accepted licences fails at this
  point. A clean machine therefore differs from a workstation that built
  once.
- **Disk:** observed in practice, the first build's Gradle and NDK install
  consumed most of the free space of a small build host: it needed well over
  9 GB free. Plan on the order of 20 GB free for the first build, and check
  free space before it rather than diagnosing a mid-build failure.
- **Gate:** `<TOOLS>/flutter/bin/flutter --version` reports
  `<CHANNEL_VERSION>`, and `flutter doctor -v` with the same environment
  reports the JDK and SDK you intended.

## 2. Make the debug signing explicit, in a scratch copy only

*Replaces: editing the app's Gradle file to "just get a signed APK", then
committing it.*

- Copy or clone `<APP>` at the commit you are building into
  `<TOOLS>/build/` and work there. Without a `key.properties` and a release
  signing config, a release build either fails on the missing signing
  material or is debug-signed by the template's fallback, depending on how the
  project wired its release signing. Where the project's Gradle file refuses
  to build without a release key, set the release build type's
  `signingConfig` to `signingConfigs.debug` **in the scratch copy only**.
- **Hard boundary:** the debug-signing edit never reaches the repository. A
  committed debug-signing switch turns every later release build into a
  debug-signed one without anyone noticing.
- **Gate:** `git -C <APP> status` shows no change to the Gradle files.

## 3. Pass build-time values explicitly

- Pass each value the app reads at compile time with `--dart-define=KEY=VALUE`
  (or `--dart-define-from-file`). Values are compiled into the APK, so they
  must be **public**: a server URL, a feature flag, a certificate the app
  should trust (for example a self-signed edge certificate as base64 DER, so
  the demo build can pin it). A private key, a token or a password never goes
  there (`core/method/secrets-posture.md`).
- When the app bakes a server address into the build (a define or a bundled
  asset file), refuse a loopback or `localhost` address for a device build: a
  phone cannot reach the build machine's loopback, and the APK fails only on
  the device. Build per target address and name the file after it.
- Build: `PATH=<TOOLS>/flutter/bin:$PATH GRADLE_USER_HOME=… PUB_CACHE=… ANDROID_HOME=<ANDROID_SDK> flutter build apk --release <DEFINES>`.
- **Gate:** the build ends in success and writes
  `build/app/outputs/flutter-apk/app-release.apk`.

## 4. Verify the artifact, not the command

A successful build proves a file exists. These three readings prove what it
is, and each is recorded with the build:

- `sha256sum <apk>` (or `shasum -a 256`): the identity of exactly this file,
  recorded where the demo is handed out.
- `aapt2 dump badging <apk>` from the SDK build tools (older build tools ship
  `aapt dump badging`): it prints what the manifest declares, among it the
  package name, version code and name, and the minimum and target SDK.
  Compare them with what you meant to build.
- `apksigner verify --print-certs <apk>`: verification passes, and the signer
  is the Android debug certificate (`CN=Android Debug`). A demo APK signed by
  anything else is a different artifact from the one this procedure makes.
- Publish as `<DIST>/<app>-demo-<versionName>+<versionCode>.apk`, so the file
  name says DEMO.
- **Gate not covered here:** installing on a real device and launching the
  app (`adb install`, then a smoke of the first screen). Run it when a device
  is available; otherwise record it as not run, never as passed.

## 5. The container variant, with no host toolchain

- Build from a Flutter image pinned by digest, with a JDK the app needs
  installed in it and the Android SDK with its licences accepted (step 1), in a multi-stage `Dockerfile` that copies the app source,
  applies the step 2 signing edit inside the image only, runs the step 3
  build, and exports the APK with
  `docker build --output type=local,dest=<DIST> .`.
- The same step 3 loopback refusal applies to the target address passed as a
  build argument.
- Run the step 4 verification on the exported file on the host.

## Failure classes

Only classes that recur across projects are listed; each one's mechanism is
on `library-corpus/language/flutter.md` (Android build pitfalls, Major lines).

| symptom | class | move |
|---|---|---|
| `No such property: VERSION_21 for class JavaVersion` inside a plugin's build file | a plugin needs a newer JDK, Gradle and AGP than the app has | raise JDK, Gradle and AGP together from the compatibility tables |
| `Unsupported class file major version …` | Gradle is older than the JDK running it | pick a JDK that Gradle supports, or raise Gradle |
| `Setting the namespace via the package attribute … is no longer supported` | a plugin predates AGP 8's namespace rule | upgrade the plugin; the fallback-namespace hook is a stopgap |
| the build asks for an SDK platform that is not installed | a plugin raised its `compileSdk` | `sdkmanager --install "platforms;android-<n>"`, or pin the plugin |
| a signing error naming `key.properties` | the step 2 scratch-copy edit is missing | step 2 |
| the app works on the emulator but cannot reach the server on a phone | a loopback address was baked into the build | step 3 |

## Reference files

- `library-corpus/language/flutter.md` (Android build, pitfalls, AGP major
  lines, security defaults)
- `core/method/secrets-posture.md` (nothing secret in a define or an asset)
- `protocols/verify.md` (verify the artifact; a gate not run)
