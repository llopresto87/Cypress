# Respawn — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Respawn is a test-database reset library for .NET integration tests. It
resets a database's **data** between tests and leaves the schema in place, so
it avoids dropping and recreating anything. That keeps each test isolated
against a real database without the cost of a full schema rebuild per test,
which is what makes database-backed integration suites fast enough to run
routinely. It resets at the start of a test, not the end, so every test starts
from a known state even when data arrived from somewhere else. It supports SQL
Server, PostgreSQL, MySQL, Oracle, Informix, DB2, SQLite and Snowflake
through database adapters (the last three from the 7.x line). Licence: Apache-2.0.

## Install, setup and configuration
- `dotnet add package Respawn`, in the test project, next to the ADO.NET
  provider of the database under test.
- `RespawnerOptions` (all `init` properties), with defaults:
  - `SchemasToInclude` / `SchemasToExclude` (default: empty, so every
    schema): scope the reset to the application's own schemas.
  - `TablesToInclude` / `TablesToIgnore` (default: empty): limit or protect
    single tables. Entries are `Respawn.Graph.Table`, which converts
    implicitly from a string (`"orders"`) and takes a schema through
    `new Table("audit", "events")`.
  - `DbAdapter`: which SQL dialect to generate. Its default differs between
    major lines (see Major lines); set it explicitly to stay independent of
    that.
  - `WithReseed` (default `false`): also reset identity columns and
    sequences.
  - `CheckTemporalTables` (default `false`): on SQL Server, turn system
    versioning off around the reset.
  - `CommandTimeout` (default: the provider's): the timeout of the reset
    command, which matters on large databases.
  - `FormatDeleteStatement` (7.x): replace the statement generated per
    table.

## Core API / usage shape
- Build a respawner once against a live, open connection:
  `await Respawner.CreateAsync(connection, new RespawnerOptions { SchemasToInclude = ["public"], TablesToIgnore = ["__EFMigrationsHistory"], DbAdapter = DbAdapter.Postgres })`.
  Creation reads the database metadata to work out the tables and the order
  their foreign keys require, so it is the expensive step. It throws when it
  finds no tables at all, which usually means the migrations have not run yet.
- Call `await respawner.ResetAsync(connection)` per test to return the
  database to its post-migration baseline. `ResetAsync` is the cheap step.
- The generated SQL depends on the adapter. SQL Server gets one `DELETE`
  per table, in foreign-key order (`DeleteSql` shows what any other adapter
  generates). PostgreSQL gets one
  `TRUNCATE ... CASCADE` over all tables in scope. Either way the tables do not
  have to be listed in dependency order by hand. Cyclic foreign keys get their
  constraints or triggers turned off for the reset.
- The whole reset runs in one transaction: it applies completely or not at
  all.
- `respawner.DeleteSql` and `respawner.ReseedSql` expose the generated SQL
  for inspection.

## Idioms & best practices
- Own the respawner in a shared test fixture so creation happens once and every
  test pays only the reset (`xunit.md` owns the collection-fixture mechanism).
  Create it after the migrations have run, since it only sees tables that
  exist at creation time.
- Reset before each test, not after, so a test that crashed mid-way cannot
  leave dirt for the next one.
- Treat the ignore list as part of the schema contract: whoever adds a
  seed/reference table also adds it to the ignore list in the same change.
- Always ignore the migration-history table (`__EFMigrationsHistory` for EF
  Core), or the next migration run will try to apply everything again.
- Re-seeding reference data after each reset is an alternative to ignoring the
  table, and it keeps the data under test control. Observed in practice: the
  cost is a second contract, since removing the re-seed step brings back the
  wiped-seed failure below. Upstream is silent on re-seeding.

## General pitfalls
- **A newly added seed table silently gets wiped:** reference/seed data that is
  not in `TablesToIgnore` survives only until the first reset. The test that runs
  before that reset passes, so the failure surfaces later and elsewhere: every
  subsequent test that depends on the seed data breaks, with nothing pointing back
  at the reset as the cause. Adding a seed table without updating the ignore list
  is the classic way to poison a whole suite.
- **A table that refuses deletion stops the whole reset.** Observed in
  practice: a table guarded by a trigger that rejects removal (an append-only
  ledger, say) makes `ResetAsync` fail unless the table is in
  `TablesToIgnore`, and the single transaction then rolls back every other
  table too. Once ignored, its rows persist across tests, so tests that write
  to it must use unique keys. On PostgreSQL the reset issues `TRUNCATE`.
  The PostgreSQL docs say `TRUNCATE` fires `ON TRUNCATE` triggers and skips
  `ON DELETE` triggers, so there only a guard that covers `TRUNCATE` blocks
  the reset.
- **`TRUNCATE ... CASCADE` reaches past the ignore list on PostgreSQL.**
  `CASCADE` also truncates every table with a foreign key that references a
  truncated table (PostgreSQL docs). An ignored table that references a table
  in scope is emptied anyway. Keep protected tables free of foreign keys into
  reset tables, or include their parents in the ignore list as well.
- A table created after `CreateAsync` ran is not reset. Rebuild the
  respawner when the schema changes during a run.
- Without `WithReseed`, identity values keep counting up across tests, so a
  test must not assert on a literal generated id.

## Testing
- Respawn is itself test infrastructure. Check the generated script once
  (`respawner.DeleteSql`) when the schema scope changes, to confirm that no
  protected table is in it.
- A useful guard test: after `ResetAsync`, assert that each reference table
  still has its rows.

## Security defaults
Respawn has no notion of a test database. It deletes or truncates every table
the connection can reach inside the configured scope, so a connection string
that points at a shared or production database destroys its data. Upstream
documents no safeguard. Build the connection from the test fixture (a
container's connection string, for example), never from shared configuration.

## Operational behaviour
- `CreateAsync` queries metadata and builds the table graph once; `ResetAsync`
  runs one command batch in one transaction.
- On PostgreSQL, `TRUNCATE` takes an `ACCESS EXCLUSIVE` lock on every table
  it touches, so a reset blocks, and is blocked by, any other open
  transaction on those tables. Tests that run in parallel against one
  database and reset it wait on each other or fail; give each parallel
  collection its own database, or run the database-backed tests in one
  collection.
- The connection passed to `CreateAsync` and `ResetAsync` must be open, and
  Respawn does not close it.

## Interop
- PostgreSQL in a container: `Testcontainers.PostgreSql.md` starts the
  database once per collection, and Respawn resets it per test.
- EF Core migrations create the schema first, and the history table goes on
  the ignore list (`Microsoft.EntityFrameworkCore.md`).
- Npgsql provides the `NpgsqlConnection` that the 7.x line recognizes for
  adapter inference (`Npgsql.md`).
- ASP.NET Core integration tests reset through the factory's fixture
  (`Microsoft.AspNetCore.Mvc.Testing.md`).

## Major lines

### 6.x line
- `RespawnerOptions.DbAdapter` defaults to `DbAdapter.SqlServer`. Any other
  database needs `DbAdapter = DbAdapter.Postgres` (or the matching adapter)
  set explicitly, or the generated SQL is SQL Server syntax.
- `Respawner.CreateAsync(string connectionString, ...)` and
  `ResetAsync(string connectionString)` overloads exist for SQL Server only.

### 7.x line
- `DbAdapter` is nullable and inferred from the connection type
  (`SqlConnection`, `NpgsqlConnection`, `MySqlConnection`, `OracleConnection`,
  `SqliteConnection` and others). An unrecognized connection type throws, and
  setting `DbAdapter` explicitly still works. `DB2Connection` maps to the
  Informix adapter; pick `DbAdapter.DB2` explicitly for DB2.
- The connection-string overloads are gone; pass an open `DbConnection`.
- `FormatDeleteStatement` lets the caller change the statement per table.
- DB2, SQLite and Snowflake adapters join the SQL Server, PostgreSQL, MySQL,
  Oracle and Informix ones.

## Upstream docs
- Repo and README: https://github.com/jbogard/Respawn
- Package: https://www.nuget.org/packages/Respawn
- PostgreSQL `TRUNCATE` semantics: https://www.postgresql.org/docs/current/sql-truncate.html
