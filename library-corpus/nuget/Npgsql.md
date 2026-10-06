# Npgsql — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

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
- Keep error-detail and parameter-logging switches out of every deployed
  configuration. They are for local debugging only (see General pitfalls).

## General pitfalls
- The connection-string keyword `Include Error Detail=true` puts the server's
  error and notice detail on `PostgresException.Detail`, and upstream warns it
  can contain sensitive data: the values involved in a failed statement. The
  exception carries it into logs.
  `NpgsqlDataSourceBuilder.EnableParameterLogging()` does the same for the
  parameters of logged commands. A committed default connection string that
  carries the keyword is inherited by anyone who runs the service without
  overriding it. The general rule for client-side error-detail switches lives
  in `../container/postgres.md`.

## Upstream docs
- https://www.npgsql.org/doc/index.html
- https://www.npgsql.org/doc/connection-string-parameters.html
- https://github.com/npgsql/npgsql
- https://www.nuget.org/packages/Npgsql
