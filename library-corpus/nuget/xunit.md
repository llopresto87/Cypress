# xunit — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A .NET unit-testing framework. Tests are plain methods marked with attributes;
the test class itself is the per-test fixture (constructed fresh per test), and
richer setup is expressed through fixture and collection types rather than
setup/teardown attributes. The runner parallelizes work across test collections
by default.

## Core API / usage shape
- `[Fact]` marks a parameterless test. `[Theory]` marks a data-driven test,
  fed by `[InlineData]` for literal cases or `[MemberData]` for cases computed
  from a property or method.
- The test class constructor is per-test setup and `IDisposable` is per-test
  teardown; `IAsyncLifetime` provides async setup/teardown that a constructor
  cannot express.
- `[CollectionDefinition]` plus `ICollectionFixture<T>` shares one expensive
  fixture instance across every test in a collection, and makes that
  collection run serially with respect to itself.

## Idioms & best practices
- Reach for a collection fixture only for genuinely expensive shared state
  (a container, a server, a database); per-test construction is the default
  and keeps tests independent.
- Keep `[Theory]` cases small and meaningful — a data row should name a
  distinct behavior, not just permute inputs.

## General pitfalls
- Parallelism is across collections, not within them: only tests grouped into
  the same fixture-scoped collection are serialized against each other. Tests
  in different collections that touch the same external resource will still
  race.
- CLI test filtering by name or trait generally needs a "contains"-style
  operator rather than exact match. An exact-match filter that matches nothing
  runs zero tests and still exits successfully — a false "all passed." Always
  confirm the executed-test count, not just the exit code.

## Upstream docs
- https://xunit.net/
- https://github.com/xunit/xunit
- https://www.nuget.org/packages/xunit
