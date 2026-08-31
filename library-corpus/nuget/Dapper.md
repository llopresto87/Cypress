# Dapper — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A micro-ORM for .NET that executes raw, parameterized SQL and maps results to
objects. It works over an ADO.NET `IDbConnection` (e.g. Npgsql,
SqlConnection) rather than replacing it.

## Core API / usage shape
- Extension methods on `IDbConnection` are the canonical surface:
  `Query<T>`/`QueryAsync<T>`, `QueryFirstOrDefault<T>`/`QueryFirstOrDefaultAsync<T>`,
  `Execute`/`ExecuteAsync`, and `ExecuteScalar<T>`/`ExecuteScalarAsync<T>`.
- Each has both plain-string overloads and `CommandDefinition`-based overloads;
  `CommandDefinition(sql, param, transaction, cancellationToken)` lets a call
  carry an explicit `IDbTransaction` and `CancellationToken`.
- Parameters are passed as an anonymous or typed object and bound by name.

## Idioms & best practices
- Values reach the database only through the `param` object, never through
  string concatenation or interpolation into the SQL text — the driver page
  (`Npgsql.md`) owns the parameterization rule this enforces.
- Flow an `IDbTransaction` and `CancellationToken` through `CommandDefinition`
  when a call participates in a transaction or must be cancellable.

## General pitfalls
- Dapper maps by matching result column names to member names; mismatches
  silently leave members unset. Alias columns in SQL to match your type.
- `DateOnly`/`TimeOnly` mapping has historically been unreliable — verify
  support before relying on native mapping of those types.

## Upstream docs
- https://github.com/DapperLib/Dapper
- https://www.learndapper.com/ (community-run guide)
- https://www.nuget.org/packages/Dapper
