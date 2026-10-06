# flutter_secure_storage — pub

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). A plant can adopt this page instead of scouting
> the plugin's surface; it still runs `ingest-library` against its own
> `pubspec.lock` for the exact version, because the Android storage scheme
> differs by major line.

## What it is
`flutter_secure_storage` is a Flutter plugin that stores key/value strings in
each platform's secure storage: the Keychain on iOS and macOS, KeyStore-backed
encryption on Android, libsecret on Linux, encrypted files on Windows, and
WebCrypto-encrypted values in browser storage on web. It is a federated plugin
(platform interface plus darwin, linux, windows and web implementations,
resolved automatically) under the BSD-3-Clause licence.

Upstream home: https://pub.dev/packages/flutter_secure_storage and
https://github.com/juliansteenbakker/flutter_secure_storage . The README on the
default branch describes the newest line; the CHANGELOG is the record of what
changed per major.

## Install, setup and configuration
- Add `flutter_secure_storage` to `dependencies`. Call
  `WidgetsFlutterBinding.ensureInitialized()` in `main` before using it, since
  it talks over a method channel.
- iOS and macOS: add the `keychain-access-groups` entitlement (an empty array
  is enough) to both the Debug and the Release entitlements; with App Groups,
  add `$(AppIdentifierPrefix)<group>`. On macOS without Keychain Sharing,
  `MacOsOptions(usesDataProtectionKeychain: false)` avoids the entitlement and
  the provisioning-profile requirement.
- Linux needs D-Bus, a Secret Service implementation (GNOME Keyring or KDE
  Wallet) and libsecret (`libsecret-1-0` at runtime, `libsecret-1-dev` to
  build). Windows needs the C++ ATL libraries from the Visual Studio Build
  Tools.
- Options: `FlutterSecureStorage(aOptions: AndroidOptions(...),
  iOptions: IOSOptions(...), mOptions: MacOsOptions(...),
  webOptions: WebOptions(...))`, on the constructor or per call.
- Defaults by platform:
  - iOS accessibility `unlocked`: items are readable only while the device is
    unlocked.
  - Android, from the 10 line: RSA-OAEP key wrapping plus an AES-GCM storage
    cipher. On the 8 and 9 lines: an AES key wrapped by an RSA key held in the
    KeyStore, with `encryptedSharedPreferences` (Jetpack Security) as opt-in.
  - `resetOnError` is true from the 10 line: an unrecoverable key-storage error
    wipes the storage instead of throwing.

## Core API / usage shape
- `write(key:, value:)`, `read(key:)` (returns `String?`, null for a missing
  key), `delete(key:)`, `containsKey(key:)`, `readAll()` and `deleteAll()`.
- Values are strings only; serialize anything else yourself (JSON, base64).
- iOS and macOS accessibility values: `unlocked` (default), `first_unlock` and
  `first_unlock_this_device`. The enum is `IOSAccessibility` on the 8 line and
  `KeychainAccessibility` in the current README; check the name on your line.
- Android biometrics: `AndroidOptions.biometric(enforceBiometrics: ...,
  biometricPromptTitle: ...)`, with the `USE_BIOMETRIC` permission (and
  `USE_FINGERPRINT` for API 23 to 27). `enforceBiometrics: true` needs API 28,
  and strong-only is fully enforced from API 30.
- Web: `WebOptions(wrapKey: ..., wrapKeyIv: ...)` wraps the stored key with an
  app-specific key, and `useSessionStorage` keeps values in session storage
  instead of local storage.
- `registerListener()` reports changes to a key.

## Idioms & best practices
- Store tokens and other secrets here, never in `shared_preferences` or plain
  files.
- Keep one storage facade that owns the single `FlutterSecureStorage` instance,
  its options and the serialization, so options live in one place (observed in
  practice; the docs are silent).
- Decide the Android options once, on the constructor. The 8-line README warns
  that mixing per-call options (`encryptedSharedPreferences`) causes errors.
- Use `first_unlock` (or `first_unlock_this_device`) when a background task,
  such as a token refresh, must read a secret while the device is locked.
- Upgrade one major at a time: upstream tells you to pass through the 10 line
  before the 11 line so stored data migrates.

## General pitfalls
- Web is not secure storage. Upstream calls the web implementation
  "experimental ... Use at your own risk": the browser holds the key, values
  sit encrypted in the same origin's storage, and any script on the origin (an
  XSS payload, a compromised third-party script) can read them. Upstream says
  HSTS and proper security headers are "VERY important". `wrapKey` is
  obfuscation only, since its value ships in the bundle.
- Web needs a secure context. WebCrypto (`window.crypto.subtle`) exists only on
  HTTPS or `localhost`, and the README says the web backend "only works" there.
  Observed in practice in a real browser over plain HTTP: the login call
  returned 200, the token write failed with no API-level error, and the app
  returned to the logged-out state about a second later. The docs do not
  describe that silent failure.
- Android Auto Backup can restore encrypted data onto a device whose KeyStore
  key differs, which fails with `java.security.InvalidKeyException: Failed to
  unwrap key`. Set `android:allowBackup="false"` or exclude the plugin's
  storage file in the backup rules.
- Changing the Android storage scheme moves the storage; values written under
  the old scheme are orphaned unless they are migrated, which forces a re-login
  at best.
- iOS and macOS: a missing `keychain-access-groups` entitlement (or a missing
  App Group) makes a write look successful while nothing is stored.
- The `resetOnError` default turns a corrupted key into silent data loss: the
  stored tokens disappear and the user is logged out.
- A direct jump across two majors on Android can lose data written under
  algorithms the newer line removed; `checkUpgradeStatus()` (11 line) reports
  that loss.

## Testing
- Upstream's own tests are integration tests in the `example` app, run with
  `flutter drive --target=test_driver/app.dart`.
- In unit tests, mock the app's own storage facade, not the plugin (observed in
  practice; the plugin sits behind a method channel).
- Prove web behaviour in a real browser served over HTTPS; a unit test cannot
  show the secure-context failure.
- Upstream documents no unit-test mocking pattern; that part is a gap.

## Security defaults
- Android 10 line and later: RSA-OAEP (SHA-256, MGF1) wraps an AES-GCM key held
  through the KeyStore; `AndroidOptions.biometric()` uses a KeyStore AES key.
- iOS: accessibility `unlocked` by default.
- Web: same-origin encrypted browser storage with a browser-held key; depends on
  HTTPS, HSTS and a content security policy. Keep token lifetimes short.
- `resetOnError` true (10 line on) prefers wiping storage to failing.
- Auto Backup on Android is the plugin's main data-leak path; see Pitfalls.

## Operational behaviour
- From the 10 line, `migrateOnAlgorithmChange` migrates data written under older
  Android ciphers, including 9-line `encryptedSharedPreferences` data. `migrateWithBackup: true` makes the migration
  crash-resistant (backup copies with a `_BACKUP` suffix, per-key `_MIGRATED`
  markers). The README is inconsistent about both defaults; test the migration
  on the line you pin.
- On the 11 line, `storageNamespace` replaces `sharedPreferencesName`, and
  `deleteAll` is scoped to the key prefix.
- Linux, from the 11 line: orphaned keyring data fails closed, and a missing
  default keyring is handled.

## Interop
- Platform floors rise by line: Java 17 and Android `minSdk` 23 on the 10 line,
  `minSdk` 24 on the 11 line; iOS 12 from the 10 line; macOS 10.14 since the 8 line.
- Works in Flutter web Wasm builds from the 10 line.
- The secure-context rule and the Android Auto Backup default are general
  Flutter facts (`library-corpus/language/flutter`); an HTTP client's auth
  interceptor (`library-corpus/pub/dio`) is the usual reader of the stored
  token.
- Unofficial pure-Dart Linux implementations exist without interop guarantees.

## Major lines
### 8
Windows moved from the credential store to encrypted files. Android: RSA-wrapped
AES by default, `encryptedSharedPreferences` opt-in; options should be set on
the constructor.

### 9
Windows rewritten on FFI. A privacy manifest for Apple platforms; the
accessibility option applies to every operation; change listeners; web
`wrapKey`/`wrapKeyIv`. Android defaults are those of the 8 line: the changelog
records no Android default change in 9, so a claim that 9 changed them is
wrong.

### 10
Android rewritten with its own ciphers (RSA-OAEP plus AES-GCM by default);
`encryptedSharedPreferences` deprecated with automatic migration;
`resetOnError` true; `AndroidOptions.biometric()`; iOS and macOS merged into
one darwin package; Java 17; `minSdk` 23; web `useSessionStorage`; Wasm
support.

### 11
Breaking: the old Android algorithms (`RSA_ECB_PKCS1Padding`,
`AES_CBC_PKCS7Padding`), the `encryptedSharedPreferences` parameter and
`sharedPreferencesName` are removed, and data under them is unusable unless
the app first ran on the 10 line. `minSdk` 24. `checkUpgradeStatus()` reports
lost data, and biometrics can be required per operation.

## Upstream docs
- https://pub.dev/packages/flutter_secure_storage
- https://github.com/juliansteenbakker/flutter_secure_storage
- https://github.com/juliansteenbakker/flutter_secure_storage/blob/develop/flutter_secure_storage/README.md
- https://github.com/juliansteenbakker/flutter_secure_storage/blob/develop/flutter_secure_storage/CHANGELOG.md
- https://developer.android.com/identity/data/autobackup
