# Microsoft.EntityFrameworkCore — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
.NET's core object-relational mapper. A `DbContext` exposes `DbSet<T>`
properties, tracks changes to the entities it materializes, translates LINQ
queries into SQL through a database provider, and persists tracked changes on
`SaveChanges`. Model shape is declared through a fluent configuration surface
(with attribute-based configuration as an alternative), and schema evolution is
expressed as migrations generated from that model.

## Core API / usage shape
- `IEntityTypeConfiguration<T>` puts each entity's mapping in its own class;
  `modelBuilder.ApplyConfigurationsFromAssembly(...)` discovers them, keeping
  `OnModelCreating` from becoming a monolith.
- `AsNoTracking()` on read-only query paths skips change-tracker bookkeeping —
  the default choice for queries whose results are never saved back.
- `ExecuteUpdateAsync` / `ExecuteDeleteAsync` issue set-based UPDATE/DELETE
  statements directly, without materializing entities or round-tripping them
  through the change tracker.
- `HasConversion(...)` maps a value object or domain-typed property to a
  primitive column, keeping the domain type out of the storage shape.

## Idioms & best practices
- Treat the `DbContext` as a short-lived unit of work, scoped to a request or
  operation, rather than a long-lived shared object.
- Prefer explicit projection to the shape a caller actually needs over loading
  full entity graphs and discarding most of them.
- Keep migrations generated from the model and reviewed as code, so the schema
  history stays a readable record rather than an opaque artifact.

## General pitfalls
- EF Core can warn that the model has changes not yet captured in a migration
  (`PendingModelChangesWarning`). Suppressing that warning to make a build or
  test run green lets model and schema diverge silently, and the drift ships to
  production undetected — fix the migration instead of silencing the warning.

## Upstream docs
- https://learn.microsoft.com/en-us/ef/core/
- https://github.com/dotnet/efcore
- https://www.nuget.org/packages/Microsoft.EntityFrameworkCore
