# flutter — language

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). A plant can adopt this page instead of scouting
> Flutter's surface; it still runs `ingest-library` against its own
> `pubspec.yaml` and `pubspec.lock` for the exact SDK, its advisories and its
> deprecations.

## What it is
Flutter is Google's cross-platform UI toolkit. Applications are written in the
**Dart** language (`library-corpus/language/dart`) and describe their interface
as a **widget tree** that Flutter's own engine renders on Android, iOS, web and
desktop from one codebase. The SDK bundles a full Dart SDK, the widget library,
hot reload, the `flutter` and `dart` CLIs and the `flutter_test` framework, so a Flutter
project needs no separate Dart install, and the Flutter release decides which
Dart it runs. Package metadata lives in `pubspec.yaml` (the `flutter` SDK
dependency is declared there as `flutter: sdk: flutter`), resolution in
`pubspec.lock`, and packages come from pub.dev.

Upstream home: the docs at https://docs.flutter.dev/ and the source at
https://github.com/flutter/flutter (BSD-3-Clause).

Flutter ships on three channels, in increasing order of stability: `master`
(tip of tree, for contributors only), `beta` (branched from `master` monthly)
and `stable` (roughly every third beta is promoted, so a new stable arrives
about quarterly). Upstream recommends `stable` "for new users and for
production app releases". Flutter publishes no support window and no
long-term-support line: a stable release *may* get a hotfix for a high-severity
or security issue, and the guidance for a bug on an older stable is to move to
the latest. Upgrading is a deliberate decision, and no end-of-life date can be
derived for a release.

## Install, setup and configuration
- Install the SDK from the official archive and put `flutter` on the path.
  `flutter doctor -v` reports the toolchains it found, including which Java
  the Android build uses. `flutter doctor --android-licenses` accepts the
  Android SDK licences.
- `flutter create` generates a runnable starter app: `lib/main.dart`,
  `pubspec.yaml`, one runner folder per platform (`android/`, `ios/`, `web/`
  and the desktop folders) and a default `test/widget_test.dart`. It writes
  `com.example.<name>` as the Android `applicationId`/`namespace` and the iOS
  `PRODUCT_BUNDLE_IDENTIFIER`.
- `pubspec.yaml` `environment:` holds two separate constraints on two separate
  SDKs. `sdk:` bounds the Dart SDK and is required; its semantics, pre-release
  bounds and the lockfile's `sdks:` block are on the dart page. `flutter:`
  bounds the Flutter SDK, so constraining Dart alone does not pin Flutter. Pub
  checks `flutter:` only when it runs under the `flutter` executable, and how
  much of the constraint it enforces depends on the root package's Dart
  language version (the `sdk:` lower bound):
  - before Dart language 3.9, pub enforces only the lower bound of `flutter:`;
  - from Dart language 3.9, the root package's upper bound is enforced too (a
    root pinned to one Flutter release fails `pub get` on any other), while the
    upper bound in a package used as a dependency is still ignored.
  The pubspec reference page still says "lower bound only"; the language
  evolution page states the 3.9 rule, which is the newer one.
- `version: x.y.z+n` in `pubspec.yaml` supplies the Android `versionName` and
  `versionCode` and the iOS build name and number. `--build-name` and
  `--build-number` on `flutter build` override it.
- `flutter config --jdk-dir=<path>` chooses the JDK for Android builds. Without
  it Flutter uses the JDK bundled with Android Studio; without Android Studio
  it uses `JAVA_HOME`, then any `java` on the path, and `flutter doctor -v`
  shows which one it picked. The setting is user-global: it applies to every
  project on the machine.
- Web: `flutter build web` writes `build/web`. Renderer and engine options are
  set at startup through `engineInitializer.initializeEngine({...})`:
  `renderer` (`'canvaskit'` or `'skwasm'`), `canvasKitBaseUrl` (where
  `canvaskit.wasm` is fetched from), `canvasKitVariant` (`auto`, `full`,
  `chromium`), `canvasKitForceCpuOnly` and `canvasKitMaximumSurfaces`.
  Android build settings are in the Android build section below.

## Core API / usage shape
- Widget tree: everything on screen is a widget. UI is built by composing
  `StatelessWidget` and `StatefulWidget` subclasses, rebuilt declaratively when
  state changes.
- CLI: `flutter pub get`, `flutter run`, `flutter analyze`, `flutter test`,
  `flutter build web|apk|appbundle|ipa`, `flutter clean`. `flutter build`
  builds in release mode unless told otherwise.
- Web output: `flutter build web` compiles Dart to JavaScript and serves a
  bootstrap (`flutter.js`) plus a renderer runtime. `--wasm` adds a
  WebAssembly build; when the browser lacks WasmGC at runtime, the JavaScript
  output is used as the fallback. `--source-maps` and `--no-strip-wasm` help
  debug a production web build.
- Platform channels: a `MethodChannel` connects Dart to native code. Its name
  must be unique in the app and identical on both sides, and reverse-domain
  naming is the convention. `StandardMessageCodec` carries null, bool, int,
  double, String, `Uint8List`, List and Map; pass a map for several arguments.
  Use `pigeon` to generate type-safe channel code for a larger surface.
- Dart may call a channel only from the root isolate, or from a background
  isolate registered with
  `BackgroundIsolateBinaryMessenger.ensureInitialized(RootIsolateToken)`.
  Native handlers run on the platform main thread; move long native work to a
  background task queue (`makeBackgroundTaskQueue()`) or a native worker
  thread.
- Release and obfuscation: `--obfuscate --split-debug-info=<dir>` (release
  only) renames Dart symbols; keep the symbol directory to read crash traces
  with `flutter symbolize -i <trace> -d <symbols>`. Obfuscation does not
  encrypt resources and does not protect against reverse engineering.
- Code that targets web and native from one codebase isolates `dart:io` behind
  a conditional import or export (the dart page has the syntax) and checks
  `kIsWeb` before reading `Platform.*`.

## Idioms & best practices
- Compose small widgets and prefer `const` constructors; let the declarative
  rebuild drive the UI from state. Keep business logic out of widgets in a
  state-management layer (`library-corpus/pub/flutter_bloc` is one).
- Build releases from the `stable` channel. Pin a pair: a stable Flutter
  release plus the Dart it bundles. Declare `environment: flutter:` as well as
  `sdk:`, because the Dart constraint says nothing about which Flutter is
  acceptable. The lockfile does not record the toolchain that built an
  artifact; the dart page says how to record it.
- Route every platform question through one small shim that checks `kIsWeb`
  first, and guard native-only initialization (push messaging, BLE or other
  vendor SDKs, `dart:io`) behind it, so the web build starts.
- Rebrand `applicationId`/`namespace` and `PRODUCT_BUNDLE_IDENTIFIER` away from
  `com.example.*` before the first store upload; a store treats the identifier
  as permanent once published.
- `flutter build` runs neither the analyzer nor the formatter; the format and
  analyze gate is on the dart page.
- Every native channel handler answers every call with `result.success`,
  `result.error` or `result.notImplemented`, and unknown method names fall
  through to `notImplemented()`. On the Dart side, catch `PlatformException`.
- When a vendor SDK is bridged through a hand-written `MethodChannel`, audit
  handler coverage per platform: list every `invokeMethod` name on the Dart
  side against the Android and the iOS handler branches. Wrap each channel call
  in a Dart `.timeout(...)`, and resolve from the SDK's callbacks, never from a
  fixed sleep. (Observed in practice on a BLE vendor SDK; the channel docs
  require the answer, and the per-platform audit and timeout are the plant's
  own practice.)
- Treat a plugin that is a fork of an abandoned package, or a vendored binary
  with no source, as a recorded risk: it has no update path, and its build
  settings can set the whole Android toolchain floor.
- docs.flutter.dev describes only the current stable, and each breaking-change
  page says it is accurate for its own release. On a pinned older SDK, check
  when an API was introduced (release notes) before relying on it.

## General pitfalls
- A scaffolded app is not a built app. A fresh Flutter project is easy to spot:
  the stock counter demo in `main.dart` ("You have pushed the button this many
  times"), the generated `test/widget_test.dart` still testing that counter, and
  a `lib/` folder with no application code beyond the template. Read that as
  "the tool was initialized, the capability was never developed", never as
  evidence of a working feature.
- Once the real app replaces `main.dart`, the generated counter test pumps the
  app and looks for the counter, so `flutter test` fails by construction until
  that test is deleted or rewritten (observed in practice, more than once).
- `flutter create` run on a non-stable channel writes a pre-release Dart lower
  bound (`-…dev`, `-…beta`) into `sdk:`. Set the floor to a stable release (the
  dart page explains what such a bound admits).
- Rebuilds of large subtrees are expensive; scope state and use `const` to
  limit what rebuilds.
- A channel call that the native side never answers leaves the Dart `Future`
  pending forever, with no error. A method handled on Android but not on iOS
  hangs `await` on iOS only.
- `dart:io` in a web build fails at runtime, not at compile time; the dart
  page has the detail, and the `kIsWeb` guard above is the fix.
- Anything declared under `assets:` ships inside the build. On web that makes a
  bundled `.env` file a public URL under `/assets/`, and `--dart-define` values
  are compiled into the bundle. Neither is a place for secrets.

### Web
- The CanvasKit engine loads from a public CDN by default. The default
  `canvasKitBaseUrl` points at Google's CDN, so a client with no outbound
  internet renders a blank white page; only the browser console says "Failed to
  download any of the following CanvasKit URLs". A check run from a machine
  with internet access passes anyway. Serve the engine from the app's own
  origin: build with `--no-web-resources-cdn`, or set `canvasKitBaseUrl` to a
  local path, and run the check with public hosts blocked. (Observed in
  practice on more than one CanvasKit build; upstream documents
  `canvasKitBaseUrl` and does not describe the failure.)
- Fonts are a second CDN dependency that `--no-web-resources-cdn` does not
  cover. Observed in practice on a CanvasKit build, confirmed by reading the
  web engine's source at one revision: the renderer fetches its default font
  (Roboto) from Google's font CDN unless the app's `FontManifest.json` declares
  a family literally named `Roboto`, and no flag turns the fetch off, so
  bundling a `Roboto` family is the fix. A separate fallback queue fetches Noto
  faces from the same CDN for any code point no bundled font covers (emoji,
  non-Latin scripts); a failed fetch only logs a warning. Bundle the Noto faces
  the content needs. The Flutter docs do not describe either fetch; re-check on
  the engine you run.
- Browser crypto and storage APIs that plugins rely on (`window.crypto.subtle`)
  exist only in a secure context (HTTPS or `localhost`). Served over plain
  HTTP, a plugin that needs them fails at runtime, often silently
  (`library-corpus/pub/flutter_secure_storage` has the worst case).
- A Flutter web client is subject to browser CORS and TLS-trust rules that the
  same app on native is not: native requests carry no `Origin` and are not
  CORS-checked. Serving the bundle from the same origin as the API (an empty or
  relative base URL behind one reverse proxy) removes the problem. In the
  browser, a blocked or aborted request reaches Dart as a transport error with
  no HTTP status; `library-corpus/pub/dio` covers how to tell that apart from a
  server answer. (Observed in practice; this is standard browser behaviour
  applied to a Flutter client.)
- Multi-threaded Wasm rendering needs `Cross-Origin-Embedder-Policy:
  credentialless` (or `require-corp`) and `Cross-Origin-Opener-Policy:
  same-origin` on the responses; without them a Wasm build runs
  single-threaded. WasmGC needs a recent Chromium-based browser, and no iOS
  browser can run Flutter Wasm, so the JavaScript output stays the fallback.
- Current Flutter releases have no HTML renderer and no `--web-renderer` flag.
  A guide that says `--web-renderer html` predates their removal.
- A stale service worker or a cached `index.html` can keep returning browsers
  on an old bundle. Observed in practice on an older Flutter release with the
  classic loader: `index.html` carried `serviceWorkerVersion` and was the only
  update trigger, `main.dart.js` was not content-hashed, and a long cache
  lifetime on `index.html`, `flutter.js` or `flutter_service_worker.js` kept
  returning browsers on the pre-fix bundle. Safari did not clear the
  service-worker state on its own (a private window worked), while Chromium
  did; Chromium also refused to register a service worker on a self-signed
  origin. The plant served those three files with `no-store` and revalidated
  the other assets. Later Flutter releases changed the generated service
  worker, so check the current web deployment page before relying on these
  details; the HTTP side of the cache policy belongs to the web server's page.

### Android build
Flutter drives Gradle for Android. The Android Gradle Plugin (AGP) turns the
Android project into an APK or an app bundle, and Flutter's own Gradle plugins
(`dev.flutter.flutter-plugin-loader` in settings, `dev.flutter.flutter-gradle-plugin`
in the app module) add the Flutter steps. The toolchain is Flutter SDK, JDK,
Gradle wrapper, AGP, Kotlin Gradle plugin and Android SDK platforms and build
tools, and each pair has a compatibility table upstream.

- Current templates use the declarative plugin DSL: `settings.gradle(.kts)`
  declares the AGP and Kotlin plugin versions in `plugins {}`, and the app
  module applies `com.android.application`, Kotlin and
  `dev.flutter.flutter-gradle-plugin`. Older projects that use `buildscript`,
  `apply plugin` and `apply from: flutter.gradle` must be migrated by hand.
- `compileSdk`, `minSdk`, `targetSdk`, `ndkVersion`, `versionCode` and
  `versionName` default to `flutter.*` values from the Flutter Gradle plugin;
  replace them with literals to pin them or to raise `minSdk` for a plugin.
- `flutter build appbundle` (preferred for Play; output
  `build/app/outputs/bundle/release/app.aab`) and `flutter build apk` (one fat
  APK for all ABIs unless `--split-per-abi`). `--split-per-abi` adds
  `ABI_VERSION * 1000` to the version code. Recent Flutter releases set
  `abiFilters` themselves for non-debuggable builds, which can override custom
  `abiFilters` in `buildTypes` or `productFlavors`; filters set in
  `defaultConfig` are kept.
- Release signing: create an upload keystore with `keytool`, put
  `storePassword`, `keyPassword`, `keyAlias` and `storeFile` in
  `android/key.properties`, load it in `android/app/build.gradle(.kts)` before
  the `android` block, define `signingConfigs.release` before `buildTypes` and
  bind `buildTypes.release.signingConfig` to it. Run `flutter clean` after
  changing signing. Play uses two keys: the upload key signs what you upload,
  and Play App Signing signs what users download.
- R8 shrinking is on in release builds; treat it as always on (the deploy page
  both offers `--no-shrink` and says the flag has no effect).
- Raise JDK, Gradle and AGP together from the compatibility tables (AGP's
  "about" page, Gradle's compatibility matrix, the Kotlin Gradle plugin table);
  never copy version numbers from a forum answer. The AGP Upgrade Assistant in
  Android Studio and `flutter analyze --suggestions` report whether AGP, Java
  and Gradle fit together.
- Keep `applicationId` equal to `namespace` and set it explicitly; changing it
  also moves the `MainActivity` package line and directory, and Play treats a
  changed `applicationId` as a new app.

Android build pitfalls:
- The strictest plugin sets the toolchain, not the app. Each plugin is a Gradle
  subproject with its own `namespace`, `compileSdk` and Java or Kotlin target,
  and the app's build must satisfy all of them. Observed in practice: a plugin
  that targets Java 21 forced JDK 21, which forced a Gradle that runs on Java 21,
  which forced an AGP 8-generation plugin; on the older Gradle the symptom was
  `No such property: VERSION_21 for class JavaVersion` inside the plugin's
  `build.gradle`. Upstream confirms each link (Gradle's matrix, AGP's minimums)
  but states no such rule.
- "Unsupported class file major version 61" (Java 17) or "65" (Java 21) means
  the Gradle version is older than the JDK running it. Upgrade Gradle, or pick
  a JDK it supports.
- A plugin bump can raise the required `compileSdk`. Install the platform with
  `sdkmanager --install "platforms;android-<n>"` (`sdkmanager --licenses` on a
  headless machine) or pin the plugin. Observed in practice: Gradle's automatic
  download did not deliver the new platform; the docs are silent on that.
- The Kotlin Gradle plugin checks `jvmTarget` against Java
  `targetCompatibility`; on Gradle 8.0 and later
  `kotlin.jvm.target.validation.mode` defaults to `error`, and it can be set to `warning` or `ignore`. Use that only as a stopgap.
- The `flutter create` main `AndroidManifest.xml` has no
  `android.permission.INTERNET`. Debug builds still reach the network because
  the tooling allows it during development, so the gap shows only in release:
  a release build without the permission has no network access. Add the
  permission to the main manifest.
- Without `key.properties` and a release signing config, the template falls
  back to the debug key, so the "release" output is debug-signed. Check what
  was built before calling it a release (see Testing).
- Build state leaks outside the project: `flutter config --jdk-dir` is
  user-global, and (observed in practice; the docs are silent) Gradle
  auto-installs the NDK and CMake into the shared Android SDK. For an isolated,
  reproducible local build, set `GRADLE_USER_HOME` and `PUB_CACHE` under the
  project and check a downloaded Flutter SDK archive against the checksum in
  the official release manifest (standard Gradle and pub variables; the
  Flutter docs do not discuss isolation).
- Multidex is needed only for a `minSdk` of 20 or lower; API 21 and later
  support it natively.

### iOS release
iOS release builds need a Mac with Xcode and an Apple Developer Program
membership. Register a Bundle ID, then set the Bundle Identifier and the signing
Team on the Runner target in Xcode (automatic signing is on by default).
`flutter build ipa` writes an Xcode archive (`.xcarchive`) to
`build/ios/archive/` and the App Store bundle (`.ipa`) to `build/ios/ipa`;
`--export-method` picks ad-hoc, development or enterprise output instead. Upload
the `.ipa` with Apple's Transporter app or `xcrun altool --upload-app`, or
validate and distribute the archive from Xcode. Each upload needs a unique build
number. This page covers no other iOS build detail (CocoaPods, entitlements,
provisioning profiles).

## Testing
- `flutter_test` drives widget tests: a test pumps a widget with a
  `WidgetTester` and asserts on the rendered tree with finders and matchers.
  Test behaviour (finders, semantics), not layout internals. `flutter test`
  runs them.
- Mock a platform plugin at the app's own interface (a facade the app owns),
  because the plugin itself sits behind a method channel (observed in
  practice; the plugin docs reviewed give no unit-test pattern).
- Verify the artifact, not the command: `apksigner verify --print-certs <apk>`
  shows the signing certificate (observed in practice: the debug certificate
  reads `CN=Android Debug`), and `aapt2 dump badging <apk>` prints the package,
  version code and name, and SDK levels. Install with `flutter install`, and
  test an app bundle with `bundletool` or a Play internal track.
- Browser end-to-end tests against a CanvasKit build need the accessibility
  tree: the canvas has no DOM text or inputs at rest. Observed in practice:
  clicking the `flt-semantics-placeholder` element (through JavaScript)
  activated the semantics tree, after which role and aria-label locators
  worked; only the focused text field had a live `<input>`, so fields were
  filled by focus and type; gesture detectors ignored a synthetic DOM
  `.click()`, so a real mouse click was needed. These are engine DOM details;
  re-check on the engine you run.
- Run the web gate with public hosts blocked and assert the set of origins the
  page contacts, so a CDN fetch fails the gate instead of passing on a
  connected machine.
- Upstream documents no unit-test pattern for the Gradle files; the AGP Upgrade
  Assistant and `flutter analyze --suggestions` are the diagnostic aids.

## Security defaults
- Release mode is the default for `flutter build`; never ship a debug or
  profile build.
- Keep `key.properties` and the keystore private and out of source control.
- Do not store secrets in the app. Obfuscation is not protection, `assets:` are
  public on web, and `--dart-define` values are compiled in.
- Android Auto Backup is on by default (`android:allowBackup` defaults to true)
  and can move app data to another device; set it false, or exclude the
  sensitive files, for data that must not leave the device. On Android 12 and
  later `allowBackup="false"` disables cloud backup but may not stop
  device-to-device transfer.
- On web, the content security policy must let the renderer run. The Flutter
  docs reviewed for this page list no directive set. Recorded in practice on
  one build, unconfirmed upstream: `'wasm-unsafe-eval'` for CanvasKit or
  skwasm, plus `blob:` and a `worker-src` directive. Test the policy against
  the build you ship.
- Release builds ignore engine flags from Intent extras, which closes a
  spoofing path.

## Operational behaviour
- Startup: `main()` calls `runApp`; a plugin that uses a method channel before
  `runApp` needs `WidgetsFlutterBinding.ensureInitialized()` first. On web, the
  bootstrap loads the renderer runtime before the first frame, so an
  unreachable engine URL means no frame at all.
- Caches: the pub cache lives under `PUB_CACHE` and Gradle's caches under
  `GRADLE_USER_HOME`; both default to user-level folders. Run `flutter clean`
  after signing or Gradle changes so cached results do not survive.
- Gradle can provision a JDK for compile tasks through a toolchain block,
  separate from the JVM that runs Gradle itself.
- Failure and recovery on web: a stale service worker or a cached `index.html`
  outlives a correct deploy (see the Web pitfalls), so a deploy is finished only
  when a returning browser has picked up the new bundle.

## Interop
- Dart: the Flutter release decides the Dart release
  (`library-corpus/language/dart`).
- State management: `library-corpus/pub/flutter_bloc`; HTTP:
  `library-corpus/pub/dio`; secrets: `library-corpus/pub/flutter_secure_storage`;
  push: `library-corpus/pub/firebase_messaging`. Each plugin adds its own
  Android and iOS floors.
- Web serving: the web server in front of a Flutter web build owns the cache
  headers, COOP/COEP headers and CSP (`library-corpus/container/nginx` for
  nginx).
- Android: Flutter plugins are Gradle subprojects, so the app's AGP, Gradle,
  JDK and Kotlin plugin must satisfy every plugin at once.

## Major lines
### Android Gradle Plugin 7
The `namespace` DSL arrived late in the AGP 7 line; before it, the namespace came from
`package=` in `AndroidManifest.xml`. Older Flutter templates used the
imperative `buildscript` and `apply plugin` form.

### Android Gradle Plugin 8
- Runs on JDK 17 and needs Gradle 8 or later; the minimum Gradle rises with each
  AGP 8 minor (read AGP's compatibility table).
- `namespace` is required in the module build script, and AGP ignores
  `package=` in a manifest. An old plugin that declares only `package=` fails
  with "Setting the namespace via the package attribute in the source
  AndroidManifest.xml is no longer supported". Upgrade the plugin. Observed in
  practice as a stopgap: a root `build.gradle` `subprojects` hook that sets a
  fallback namespace for plugins without one; the docs are silent on it.
- AGP generates `BuildConfig` only when a module asks for it (AIDL and
  RenderScript are off as well); non-transitive R classes and non-final resource IDs are on. A module
  that needs `BuildConfig` enables `buildFeatures { buildConfig = true }`. The
  project-wide `android.defaults.buildfeatures.buildconfig=true` flag in
  `gradle.properties` works only on the AGP 8 line.

### Android Gradle Plugin 9
- Needs a Gradle 9 release, JDK 17 and the Kotlin Gradle plugin minimum its
  release notes name.
- The new DSL is the default and the legacy variant API (`applicationVariants`
  and kin) is removed; `android.newDsl=false` opts out until AGP 10, which makes
  the new variant API mandatory. Third-party plugins may need new versions.
- Kotlin is built in, and the `org.jetbrains.kotlin.android` plugin is not
  compatible with the new DSL. Flutter added interim support for the legacy
  Kotlin plugin under AGP 9 (`android.builtInKotlin=false`) and later support
  for `android.builtInKotlin=true` once the app and all its plugins have
  migrated; a project that never applied the Kotlin plugin has nothing to
  migrate. Read Flutter's built-in Kotlin migration page for the release you
  run.
- Other defaults change: Java source and target 11, `android.useAndroidX` true,
  `targetSdk` derived from `compileSdk`, R8 strict full mode and optimized
  resource shrinking on, and the `aidl`, `renderscript` and `buildconfig`
  default flags removed.

## Upstream docs
- https://docs.flutter.dev/
- https://github.com/flutter/flutter
- https://github.com/flutter/flutter/blob/master/docs/releases/Flutter-build-release-channels.md
- https://docs.flutter.dev/platform-integration/web/initialization
- https://docs.flutter.dev/platform-integration/web/wasm
- https://docs.flutter.dev/platform-integration/platform-channels
- https://docs.flutter.dev/deployment/android
- https://docs.flutter.dev/deployment/obfuscate
- https://docs.flutter.dev/release/breaking-changes
- https://developer.android.com/build/releases/about-agp
- https://docs.gradle.org/current/userguide/compatibility.html
- https://dart.dev/tools/pub/pubspec
- https://dart.dev/resources/language/evolution
