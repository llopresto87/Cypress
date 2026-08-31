# flutter — language

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Flutter is Google's cross-platform UI toolkit: applications are written in the
**Dart** language and describe their interface as a **widget tree** rendered by
Flutter's own engine to mobile, web, and desktop targets from one codebase. The
SDK bundles the Dart toolchain, a widget library, hot reload, and a test
framework. Package/dependency metadata lives in `pubspec.yaml`.

## Core API / usage shape
- **Widget tree**: everything on screen is a widget; UI is built by composing
  `StatelessWidget` / `StatefulWidget` subclasses in a tree, rebuilt
  declaratively when state changes.
- **Dart SDK**: the language and `dart`/`flutter` CLIs handle building, running,
  and dependency resolution (`flutter pub get`).
- **Testing**: `flutter_test` drives widget tests — the conventional
  `test/widget_test.dart` pumps a widget and asserts on the rendered tree with a
  `WidgetTester` and finders/matchers.
- **Project scaffold**: `flutter create` generates a runnable starter app —
  `lib/main.dart`, `pubspec.yaml`, platform runner folders, and a default test.

## Idioms & best practices
- Compose small widgets and prefer `const` constructors where possible; let the
  declarative rebuild model drive UI from state rather than manual mutation.
- Keep business logic out of widgets via a state-management approach; widgets
  stay thin and describe the view.
- Write widget tests against behavior (finders/semantics), not against exact
  layout internals.

## General pitfalls
- **A scaffolded app is not a built app.** A freshly generated Flutter project
  is trivially identifiable: the stock counter-demo `main.dart` (the "You have
  pushed the button this many times" template), the generated
  `test/widget_test.dart` still testing that counter, and a `lib/` folder with
  no application code beyond the template. Read that as "the tool was
  initialized, the capability was never developed", never as evidence of a
  working feature — as with any scaffolding tool, an unmodified template plus
  its own generated smoke test asserts nothing.
- Rebuilds can be expensive if large subtrees rebuild unnecessarily; scope state
  and use `const` to limit rebuild blast radius.
- The SDK version and Dart version move together and gate available language
  features (a per-project pin concern).

## Upstream docs
- https://docs.flutter.dev/
- https://dart.dev/
- https://github.com/flutter/flutter
