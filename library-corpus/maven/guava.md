# guava — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Google's core Java utility library — a broad set of general-purpose helpers that
predate or complement the JDK: immutable collections, additional collection
types, caching, functional utilities, concurrency helpers, string/`Preconditions`
utilities, hashing, and more. Canonical coordinates:
`com.google.guava:guava`.

## Core API / usage shape
- **Immutable collections**: `ImmutableList`, `ImmutableSet`, `ImmutableMap`
  and friends — allocated once, never modified, safe to share across threads.
- **Extended collections**: `Multimap`, `Multiset`, `BiMap`, `Table`, and
  `Range` cover shapes the JDK lacks.
- **`RateLimiter`**: a token-bucket style limiter that smooths or throttles the
  rate of operations (`acquire()` blocks to honor a configured permits-per-second).
- **Caches**: `CacheBuilder` / `LoadingCache` build in-memory caches with size
  bounds, time-based eviction, and automatic loading of missing entries.
- **Utilities**: `Preconditions` for argument checks, `Optional` (predating
  `java.util.Optional`), `Joiner`/`Splitter`, and hashing helpers.

## Idioms & best practices
- Reach for immutable collections as the default for shared or returned data;
  they document intent and remove a class of concurrency bugs.
- Use `LoadingCache` for read-through caching of expensive computations rather
  than hand-rolling a map with eviction.
- Prefer `RateLimiter` over a hand-rolled throttle for coarse in-process rate
  limiting.

## General pitfalls
- **`-jre` vs `-android` flavour split**: Guava ships two variants distinguished
  by a version suffix — a `-jre` flavour targeting standard JVMs and an
  `-android` flavour built for the more limited Android/older-Java surface.
  Pulling the wrong flavour (often via a transitive dependency that pinned
  `-android`) can produce subtly different behavior or missing APIs on a server
  JVM; align the classpath on the `-jre` flavour for backend services.
- `RateLimiter` is in-process only; it does not coordinate across instances, so
  distributed rate limiting still needs an external coordinator.
- Guava's `Optional` and functional types differ from the JDK equivalents;
  mixing them causes confusion — prefer the JDK types on modern lines except
  where a Guava-specific API requires its own.
- Guava has historically deprecated/removed `@Beta`-annotated APIs between
  lines; do not build durable code on `@Beta` surface.

## Upstream docs
- https://github.com/google/guava
- https://guava.dev/
- https://mvnrepository.com/artifact/com.google.guava/guava
