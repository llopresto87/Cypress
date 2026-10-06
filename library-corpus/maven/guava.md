# guava — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Google's core Java libraries: a broad set of general-purpose helpers that
predate or complement the JDK, among them immutable collections, extra
collection types (multimap, multiset), a graph library, caching, and utilities
for concurrency, I/O, hashing, primitives and strings. Coordinates:
`com.google.guava:guava`, with the flavour in the version field:
`<version>-jre` (JDK 8 or later) or `<version>-android` (an Android-compatible
subset that does not require Android; code that must work on both uses it).
The Spring Boot BOM does not manage Guava itself (only adapters such as
Caffeine's Guava module), so a project pins it or inherits whatever a
dependency brings. Upstream home: https://github.com/google/guava, user guide
"Guava Explained" on its wiki, Javadoc at https://guava.dev.

## Install, setup and configuration
- Declare `com.google.guava:guava:<version>-jre` explicitly on a server JVM.
- Guava's one runtime-linkage dependency is `com.google.guava:failureaccess`;
  the others are annotation-only and usually safe to exclude, with caveats
  around reflection.
- **Version conflicts:** upgrade to the newest Guava, or force one version for
  every dependency through dependency management. Upstream says this fails only
  when a dependency uses `@Beta` APIs or was built against Guava from before
  Guava 21.
- A library that needs `@Beta` APIs and does not expose Guava types should
  shade and relocate Guava (`maven-shade-plugin` relocation of `com.google`).
- Guava has no runtime configuration file; each object is configured through
  its builder or factory (`CacheBuilder`, `RateLimiter.create`).

## Core API / usage shape
- **Immutable collections** (`ImmutableList`, `ImmutableSet`, `ImmutableMap`,
  built with `of`, `copyOf` or builders): defensive copies, thread-safe, and
  they reject `null` elements. For nulls, wrap a null-permitting collection in
  `Collections.unmodifiableList`.
- **Extended collections:** `Multimap`, `Multiset`, `BiMap`, `Table` and
  `Range` cover shapes the JDK lacks.
- **`RateLimiter.create(permitsPerSecond)`:** `acquire()` blocks until a permit
  is free; permits are never released; it is safe for concurrent use but not
  fair; the cost of a large `acquire(n)` is paid by the next caller, not the
  current one; an optional warm-up period exists.
- **`CacheBuilder`** builds a `Cache` or `LoadingCache` with a size bound
  (`maximumSize`, `maximumWeight`), expiry (`expireAfterWrite`,
  `expireAfterAccess`), refresh (`refreshAfterWrite`), weak or soft references,
  removal listeners and statistics; entries load through a `CacheLoader` or a
  `Callable` passed to `get`.
- **Utilities:** `Preconditions` for argument checks, `Joiner`/`Splitter`,
  hashing helpers, and `com.google.common.base.Optional`, which predates and is
  incompatible with `java.util.Optional`.

## Idioms & best practices
- Make immutable collections the default for shared or returned data.
- **Prefer Caffeine for new caches.** The `CacheBuilder` Javadoc names Caffeine
  as its successor (faster, more features including async loading, fewer
  bugs; not for Android), and `CaffeinatedGuava` adapts existing Guava cache
  code.
- Use `RateLimiter` for coarse in-process throttling, for example of calls to a
  third-party API (observed in practice), instead of a hand-rolled throttle.
- Prefer `java.util.Optional` and the JDK functional types; Guava itself
  recommends the JDK class wherever possible, though it does not plan to
  deprecate its own.

## General pitfalls
- **Used but undeclared.** Observed in practice: code that calls Guava directly
  while Guava arrives only transitively (an old version brought in by an
  API-documentation library) breaks, or silently changes version, when that
  dependency is removed or upgraded. Declare it explicitly at a current `-jre`
  version. Upstream's conflict guidance does not describe this case.
- **Wrong flavour.** A transitive `-android` version on a server JVM resolves to
  the Android-compatible subset; align backends on `-jre`. Partway through the
  32 line Guava started publishing Gradle module metadata that picks the
  flavour by target, and Gradle users may then hit new variant-selection
  errors.
- **`@Beta` APIs** can change or disappear in any release, so libraries must not
  use them (the Guava Beta Checker enforces that). Non-`@Beta` APIs, deprecated
  ones included, stay binary-compatible indefinitely since Guava 21.
- **Serialized forms** of Guava objects can change between versions; never
  persist them.
- **No background cache cleanup.** `CacheBuilder` removes expired entries during
  writes (and occasionally reads), so a rarely written cache keeps stale entries
  in memory until `cleanUp()` runs. Removal listeners run synchronously by
  default.
- **`RateLimiter` is in-process only;** it does not coordinate across instances,
  so distributed limiting needs an external coordinator.
- **Nulls** make immutable-collection construction throw.

## Testing
- Test timed cache eviction with `CacheBuilder.ticker(Ticker)` and a fake time
  source instead of sleeping.
- `com.google.guava:guava-testlib` is the companion test artifact; its content
  was not checked for this page.
- Observed in practice: after making Guava explicit or bumping it across many
  versions, run the tests that exercise the used surface; the non-`@Beta`
  promise meant no call-site changes for `RateLimiter` and immutable
  collections.

## Security defaults
- Upstream says Guava classes are not designed to protect against a malicious
  caller: do not use them as a boundary between trusted and untrusted code.
- Do not deserialize Guava objects persisted by another version.

## Operational behaviour
- Cache maintenance piggybacks on normal operations: a busy cache needs nothing
  extra, a rarely written one may need a scheduled `cleanUp()`.
- Guava is tested on a range of OpenJDK versions on Linux and Windows; some
  `com.google.common.io` features may not work correctly outside Linux.
- There are no release candidates; fixes ship in the next release.

## Interop
- Caffeine (the successor cache), Jackson `jackson-datatype-guava` and AssertJ
  `assertj-guava` (both managed by the Boot BOM), and `ListenableFuture`
  through its own `failureaccess` artifact.

## Major lines
Guava uses semantic versioning: every API removal or incompatible change,
`@Beta` included, bumps the major.
- **Up to 21:** non-`@Beta` APIs could be removed after deprecation, so a
  dependency built against such an old Guava can conflict with a current one.
- **From partway through the 23 line:** each release has two version strings, `-jre` and
  `-android`.
- **From partway through the 32 line:** Gradle module metadata selects the
  flavour and handles conflicts; upstream's release notes warn that its first
  metadata release was broken.

## Upstream docs
- https://github.com/google/guava
- https://github.com/google/guava/wiki/UseGuavaInYourBuild
- https://guava.dev/releases/snapshot-jre/api/docs/
- https://github.com/ben-manes/caffeine
