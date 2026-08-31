# Testcontainers.PostgreSql — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The PostgreSQL module for Testcontainers on .NET. It starts a disposable, real
PostgreSQL instance in a container for the lifetime of a test run and hands
back its connection string. The trade is deliberate: container startup cost and
a Docker dependency, in exchange for testing against the real engine instead of
an in-memory or fake provider whose behavior diverges from PostgreSQL on
exactly the things integration tests exist to catch — SQL dialect, constraints,
transactions, concurrency, and provider-specific types.

## Core API / usage shape
- A builder configures the instance:
  `new PostgreSqlBuilder().WithImage(...).WithDatabase(...).Build()`, plus
  further `With...` calls for user, password, and other container settings.
- `StartAsync()` starts the container and `DisposeAsync()` tears it down —
  typically owned by a test fixture's lifecycle rather than called inline in a
  test.
- `GetConnectionString()` returns the connection string for the running
  instance, including its dynamically mapped host port, to hand to the code
  under test.

## Idioms & best practices
- Own the container in a shared test fixture rather than starting one per test
  (`xunit.md` owns the collection-fixture mechanism), then isolate tests from
  each other by resetting or namespacing data — transaction rollback, per-test
  schema, or truncation (`Respawn.md`) — rather than by restarting the
  container.
- Let the module assign the host port and read every connection detail off the
  running container at start time; bind and hard-code nothing fixed, so
  parallel runs and CI agents do not collide.

## General pitfalls
- It requires a running Docker daemon on the test host. Tests pass locally and
  fail in CI whenever the pipeline has no daemon provisioned, and the failure
  surfaces as an opaque connection error rather than a clear "Docker missing."
- Container startup dominates first-test latency, and the cost is paid per
  container started — which is what turns a per-test container into a slow
  suite.

## Upstream docs
- https://dotnet.testcontainers.org/
- https://github.com/testcontainers/testcontainers-dotnet
- https://www.nuget.org/packages/Testcontainers.PostgreSql
