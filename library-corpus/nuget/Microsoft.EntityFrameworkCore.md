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
- `AsNoTracking()` on read-only query paths skips change-tracker bookkeeping,
  the default choice for queries whose results are never saved back.
- `ExecuteUpdateAsync` / `ExecuteDeleteAsync` issue set-based UPDATE/DELETE
  statements directly, without materializing entities or round-tripping them
  through the change tracker.
- `HasConversion(...)` maps a value object or domain-typed property to a
  primitive column, keeping the domain type out of the storage shape.
- The migrations CLI (`dotnet ef`, the `dotnet-ef` tool) needs two projects.
  `--project` names the one that holds the migrations and references
  `Microsoft.EntityFrameworkCore.Design`/`.Tools`; `--startup-project` names the
  one the tool builds and runs to obtain a configured `DbContext`. In a layered
  solution they differ, and the CLI's guess from the current directory is
  usually wrong:
  `dotnet ef migrations add <Name> --project <data-project> --startup-project <host-project>`.
- A migration is emitted as a timestamp-prefixed file whose class name carries
  no timestamp. Name it verb-first in PascalCase (`AddOrderStatus`); the tool
  adds the timestamp to the file name only.
- Migrations can be applied three ways: `Database.Migrate()` at application
  start, a generated SQL script (`dotnet ef migrations script --idempotent`), or
  a self-contained migrations bundle (`dotnet ef migrations bundle`).

## Idioms & best practices
- Treat the `DbContext` as a short-lived unit of work, scoped to a request or
  operation, rather than a long-lived shared object.
- Prefer explicit projection to the shape a caller needs over loading
  full entity graphs and discarding most of them.
- Keep migrations generated from the model and reviewed as code, so the schema
  history stays a readable record rather than an opaque artifact.
- Record the exact `dotnet ef` invocation for the solution (both project flags
  and any environment the host needs) in the project's runbook the first time
  it is worked out, so nobody re-derives it.
- For shared or production databases, prefer applying a reviewed idempotent
  script or bundle as a deploy step over `Database.Migrate()` at startup.

## General pitfalls
- EF Core can warn that the model has changes not yet captured in a migration
  (`PendingModelChangesWarning`). Suppressing that warning to make a build or
  test run green lets model and schema diverge silently, and the drift ships to
  production undetected. Fix the migration instead of silencing the warning.
- `Database.Migrate()` at startup runs whatever migrations merged, on the first
  boot after deploy, with no review gate in between; the general rule lives in
  `../container/postgres.md`.
- `dotnet-ef` is usually a global tool, and a global tool built for a newer .NET
  major than the target fails to start where only the target's runtime is
  installed (or the reverse). The runtime roll-forward variable fixes it; that
  fact is owned by `../language/dotnet.md`. A local tool manifest pinned beside
  the solution avoids the mismatch.
- `EnableSensitiveDataLogging()` puts entity and parameter values into logs and
  exception messages. It is a local debugging aid; keep it out of every deployed
  configuration.

## Upstream docs
- https://learn.microsoft.com/en-us/ef/core/
- https://learn.microsoft.com/en-us/ef/core/cli/dotnet
- https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/applying
- https://github.com/dotnet/efcore
- https://www.nuget.org/packages/Microsoft.EntityFrameworkCore
