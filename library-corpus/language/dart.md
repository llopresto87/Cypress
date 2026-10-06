# dart — language

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). A plant can adopt this page instead of scouting
> Dart's surface; it still runs `ingest-library` against its own `pubspec.yaml`
> and `pubspec.lock` for the exact SDK and its advisories.

## What it is
Dart is a client-optimized, statically typed language with sound null safety.
It compiles to native code (a VM with a JIT for development, ahead-of-time
machine code for release) and to the web (JavaScript or WebAssembly). The SDK
ships the core libraries and the command-line tools: `dart`, `dart pub`,
`dart analyze`, `dart format`, `dart fix`, `dart test` and `dart compile`. The
manifest is `pubspec.yaml`, the lockfile `pubspec.lock`, and the package
registry is pub.dev. The Flutter SDK includes a full Dart SDK, and the Flutter
release decides which Dart it runs (`library-corpus/language/flutter`).

Upstream home: https://dart.dev , the SDK source at
https://github.com/dart-lang/sdk , the registry at https://pub.dev .

Support model: "The Dart team supports only the latest, stable version of the
Dart SDK." A new major or minor release ends support for the previous one.
Critical and security fixes ship only as patch releases of the current stable,
and a new stable arrives about every three months. Dart names no long-term
support line.

## Install, setup and configuration
- Install through a package manager (upstream's recommendation), a Docker
  image, the Flutter SDK, or a ZIP from the SDK archive. Channels are `stable`
  ("tested and approved for production use"), `beta` (not for production),
  `dev` and `main`.
- The SDK may send usage metrics and crash reports to Google;
  `dart --disable-analytics` turns that off.
- Package layout: `lib/` (public code, `lib/src/` private), `bin/`, `test/`,
  and the tool-owned `.dart_tool/`.
- `pubspec.yaml` `environment:`:
  - `sdk:` is required. Without it `dart pub get` fails with "no lower-bound
    SDK constraint".
  - The lower bound must be at least the release that introduced every
    language feature the package uses. It also sets the package's language
    version (see Language versions).
  - Caret syntax (`^3.4.0`) is accepted in `sdk:` from Dart 2.19; earlier SDKs
    need a full range (`'>=2.12.0 <3.0.0'`).
  - A `flutter:` key next to `sdk:` constrains a different SDK; its rules are on
    the flutter page.
- `dependencies` are resolved for the package and its dependents;
  `dev_dependencies` only for the package itself.
- `dependency_overrides` is for temporary development use. The docs warn that
  an override outside a package's declared range, or a local path copy,
  "involves some risk".
- `analysis_options.yaml`: `include: package:lints/recommended.yaml` (or
  `package:flutter_lints/flutter.yaml`), an `analyzer:` block for strictness
  (`strict-casts`, `strict-raw-types`, `exclude`) and `linter: rules:` for
  individual rules. Included files merge in order, and local settings win.

## Core API / usage shape
- Sound null safety: types are non-nullable unless marked `?`. Dart 3 enforces
  it with no opt-out, so a package that is not null-safe cannot resolve.
- Async: `Future`, `Stream`, `async`/`await`. Most `dart:io` operations return a
  `Future` or a `Stream`; synchronous variants carry a `Sync` suffix.
- Platform libraries: `dart:io` (files, sockets, processes, HTTP) is available
  to command-line apps, servers and non-web Flutter apps, never to web apps.
  `dart:js_interop` and `package:web` serve the web; `dart:html` is deprecated
  and unsupported when compiling to Wasm.
- Conditional imports and exports choose an implementation by library
  availability:
  `export 'src/none.dart' if (dart.library.io) 'src/io.dart' if (dart.library.js_interop) 'src/web.dart';`
- Tools: `dart pub get|upgrade|downgrade|add|outdated`, `dart analyze`,
  `dart format`, `dart fix --apply`, `dart test`, `dart compile exe|aot-snapshot|js|wasm`.

## Idioms & best practices
- Follow Effective Dart (its Style, Documentation, Usage and Design guides);
  its themes are "be consistent" and "be brief", and `dart format` owns layout.
- Gate CI on `dart format -o none --set-exit-if-changed <path>` (exit 1 when a
  file would change) and on `dart analyze` (or `flutter analyze`) with the
  `lints` or `flutter_lints` set.
- An application commits `pubspec.lock`; a library package does not.
- Set the `sdk:` floor to a stable release that covers every feature used, and
  raise it when resolution shows the dependencies need more (see Pitfalls).
- Isolate platform-specific code behind a conditional import so the same
  package compiles for native and web.
- Record why each `dependency_overrides` entry exists and when it can go; a
  permanent override is a smell (observed in practice).

## General pitfalls
- The lockfile does not pin the SDK. Observed in practice in more than one
  plant: the `sdks:` block of `pubspec.lock` records the combined SDK
  constraint the resolved packages need, never the SDK version that ran the
  resolution; it can repeat the manifest floor or sit above it. The docs
  describe the lockfile as the concrete versions and content hashes of every
  dependency and say nothing about the toolchain. Record the toolchain
  separately (`dart --version` or `flutter --version` in the build
  environment).
- The manifest floor can understate the real minimum: resolved packages may
  need a newer SDK than `environment: sdk:` admits, and the lockfile's `sdks:`
  line shows it. Raise the manifest floor to match (observed in practice; the
  docs' rule that the floor must cover the features used points the same way).
- Pre-release lower bounds. `flutter create` on a non-stable channel writes a
  floor such as `>=3.x.y-N.0.dev` or `-…beta`. By `pub_semver` rules a
  pre-release sorts below its release (`2.0.0-beta < 2.0.0`), so such a floor
  admits that pre-release and every later release, and a `<` maximum excludes
  pre-releases of the maximum unless the maximum is itself a pre-release.
  Replace the floor with a stable `^x.y.0`. That advice is observed practice
  on projects that carried such a floor; the docs do not give it.
- Raising the `sdk:` floor can reformat every file. From language version 3.7,
  `dart format` applies the "tall" style, and the style follows the package's
  language version.
- A wide SDK range (`^3.0.0`) is a compatibility declaration, not a support
  claim. Upstream supports only the latest stable whatever range a package
  admits, so a wide range is not a defect by itself (derived from the support
  policy and the pubspec rules).
- Importing `dart:io` in code that also builds for web can compile, but the
  call fails in the browser at runtime with `Unsupported operation` (observed
  in practice; the docs say only that web apps cannot use `dart:io`).

## Testing
- `package:test` with `dart test` (`flutter test` in a Flutter project). Test
  files live under `test/` and end in `_test.dart`; use `group`, `setUp` and
  `tearDown`; select with `--name`, `--tags` and `--exclude-tags`.
- Put `test` and mocking packages in `dev_dependencies`.
- The SDK ships no mocking library, and the upstream testing page gives no
  mocking guidance; a mocking package is a project choice.

## Security defaults
- Only the latest stable receives security fixes, so staying current is the
  security posture. Advisories are published in the dart-lang GitHub
  repositories, and `dart pub` surfaces advisories for dependencies unless
  `pubspec.yaml` lists the advisory under `ignored_advisories`.
- Report a vulnerability through Google's vulnerability program.
- `dependency_overrides` and path dependencies bypass resolution safeguards;
  keep them out of release builds where possible.
- Analytics: the SDK reports usage and crashes unless disabled (see Install).

## Operational behaviour
- Resolution: pub picks, for each package, the newest version whose own SDK
  constraint admits the installed SDK, and the lockfile pins the exact versions
  and content hashes. A different SDK can therefore resolve a different set
  from the same manifest when no lockfile exists.
- Compilation: `dart run` uses the JIT; `dart compile exe` produces a
  self-contained native executable; `dart compile js` and `dart compile wasm`
  target the web.
- Cadence: a stable about quarterly, patches only for the current stable. Read
  the SDK changelog for library, language and tool changes before an upgrade.

## Interop
- Flutter bundles Dart; the Flutter release decides the Dart release
  (`library-corpus/language/flutter`).
- JavaScript interop through `dart:js_interop` and `package:web`; native
  through `dart:io` and `dart:ffi`; conditional imports bridge the two.
- Lint sets come from the `lints` and `flutter_lints` packages.

## Language versions
In Dart the language version of a package is the minor version of its `sdk:`
lower bound, so a feature is available only when the floor admits it. The
lines that change what a package may write:

### Dart 2.12 and 2.19
- 2.12 introduced sound null safety (opt-in until Dart 3).
- 2.19 accepts caret syntax in `sdk:` and allows unnamed libraries.

### Dart 3
- Null safety is mandatory; language versions before 2.12 are no longer
  supported.
- New: patterns, records, class modifiers (`base`, `final`, `interface`,
  `sealed`, `mixin class`), switch expressions and if-case.
- Breaking: a class must be declared `mixin` (or `mixin class`) to be mixed in;
  a colon before a named parameter's default value is an error (use `=`); a
  `continue` label must target a loop or a switch member.

### Feature gates within Dart 3
- 3.2: private final field promotion.
- 3.3: extension types.
- 3.6: digit separators.
- 3.7: wildcard `_` variables, and the tall `dart format` style, which follows
  the language version.
- 3.8: null-aware elements in collection literals.
- 3.9: the root package's `flutter:` upper bound is enforced (flutter page).
- 3.10: dot shorthands.
- 3.12: private named parameters.
- 3.13: primary constructors.

The language evolution page is the authoritative list; check it for lines newer
than this page.

## Upstream docs
- https://dart.dev/
- https://dart.dev/tools/sdk (support policy)
- https://dart.dev/get-dart
- https://dart.dev/tools/pub/pubspec
- https://dart.dev/tools/pub/dependencies
- https://dart.dev/tools/pub/versioning
- https://github.com/dart-lang/pub_semver
- https://dart.dev/null-safety
- https://dart.dev/resources/language/evolution
- https://dart.dev/effective-dart
- https://dart.dev/tools/analysis
- https://dart.dev/tools/dart-format
- https://dart.dev/tools/dart-test
- https://dart.dev/interop/js-interop/package-web
- https://dart.dev/security
- https://github.com/dart-lang/sdk/blob/main/CHANGELOG.md
