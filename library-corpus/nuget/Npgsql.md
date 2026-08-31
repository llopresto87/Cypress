# Npgsql — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The raw ADO.NET PostgreSQL driver for .NET (`NpgsqlConnection`, `NpgsqlCommand`,
etc.). It is also the underlying provider pulled in transitively by
`Npgsql.EntityFrameworkCore.PostgreSQL` and consumed via EF Core's `UseNpgsql()`
extension.

## Core API / usage shape
- Core usage is standard ADO.NET: open an `NpgsqlConnection`, create commands
  with parameters, and execute/read results. It also underpins Dapper's
  extension methods when used as the `IDbConnection`.
- The EF Core provider extension `UseNpgsql()` comes from
  `Npgsql.EntityFrameworkCore.PostgreSQL`, which depends on the core package.
- OpenTelemetry tracing helpers `AddNpgsql()` / `AddNpgsqlInstrumentation()`
  come from the separate `Npgsql.OpenTelemetry` package, not the core package.

## Idioms & best practices
- Parameterize all SQL; never concatenate untrusted input into command text.
- When using EF Core with PostgreSQL, let Npgsql resolve transitively via
  `Npgsql.EntityFrameworkCore.PostgreSQL` rather than installing it directly, so
  the versions stay compatible.

## Upstream docs
- https://www.npgsql.org/doc/index.html
- https://github.com/npgsql/npgsql
- https://www.nuget.org/packages/Npgsql
