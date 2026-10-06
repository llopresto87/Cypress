# Dapper — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A micro-ORM for .NET that executes raw, parameterized SQL and maps results to
objects. It works over an ADO.NET `IDbConnection` (e.g. Npgsql,
SqlConnection) rather than replacing it: every call is an extension method on
the connection. It has no database-specific code and works with any ADO.NET
provider. It ships as four packages:

- `Dapper`: the library itself.
- `Dapper.StrongName`: the strong-named build of the same library.
- `Dapper.SqlBuilder`: a separate add-on for composable SQL building.
- `Dapper.Rainbow`: a separate add-on with CRUD helpers.

Licence: Apache-2.0. It started at Stack Overflow and is maintained as open
source by the DapperLib organisation.

## Install, setup and configuration
- `dotnet add package Dapper`, plus the ADO.NET provider for your database
  (`Npgsql`, `Microsoft.Data.SqlClient`, `Microsoft.Data.Sqlite`, ...). Dapper
  brings no provider of its own.
- There is no setup object. Global behaviour lives in static settings that
  apply to the whole process:
  - `SqlMapper.Settings.CommandTimeout`: default timeout for every command
    (unset, so the provider's default applies).
  - `SqlMapper.Settings.ApplyNullValues`: off by default, so a null column
    leaves the member at its initial value instead of assigning null.
  - `SqlMapper.Settings.PadListExpansions`: off by default; pads `in @list`
    expansions with nulls to limit the number of distinct query plans. Unsafe
    where null equality is enabled ("ansi nulls off").
  - `SqlMapper.Settings.InListStringSplitCount`: off by default; on SQL Server
    2016 and later, switches large integer `in` lists to `STRING_SPLIT`.
  - `SqlMapper.Settings.SupportLegacyParameterTokens`: on by default; detects
    single-character tokens such as `?`. Upstream does not recommend them and
    plans to turn the setting off by default.
  - `DefaultTypeMap.MatchNamesWithUnderscores`: off by default; when on,
    `order_id` maps to `OrderId`.
- Type handlers: `SqlMapper.AddTypeHandler(...)` registers a custom
  `TypeHandler<T>` that converts a type to and from a parameter and a column.
  Like the settings above, it is process-wide.

## Core API / usage shape
- Extension methods on `IDbConnection` are the canonical surface:
  `Query<T>`/`QueryAsync<T>` (many rows),
  `QueryFirst`/`QueryFirstOrDefault`/`QuerySingle`/`QuerySingleOrDefault`
  (one row, with the matching LINQ semantics, plus async forms),
  `Execute`/`ExecuteAsync` (returns affected rows), and
  `ExecuteScalar<T>`/`ExecuteScalarAsync<T>`.
- Each has two overload families. The plain-string overloads take
  `(sql, param, transaction, commandTimeout, commandType)`, so a transaction can
  be passed positionally or by name. They have no `CancellationToken`. The
  `CommandDefinition` overloads take
  `new CommandDefinition(sql, param, transaction, commandTimeout, commandType,
  flags, cancellationToken)`, the only way to make a call cancellable.
- Parameters: an anonymous object or POCO (members bind to `@Name` by name), a
  `Dictionary<string, object>`, or `DynamicParameters`. `DynamicParameters`
  adds an explicit `DbType`, direction (output and return values, read with
  `p.Get<T>("@name")`), and merging several objects.
- List expansion: `where Id in @Ids` with an `IEnumerable` value becomes one
  parameter per element (`in (@Ids1, @Ids2, ...)`).
- `Execute(sql, IEnumerable<T>)` runs the command once per element.
- Multi-mapping: `Query<TFirst, TSecond, TReturn>(sql, map, splitOn: "Id")`
  maps each joined row to several objects. The row splits at columns named
  `Id` unless you name another column in `splitOn`.
- Multiple result sets: `QueryMultiple` / `QueryMultipleAsync` return a
  `GridReader`; call `Read<T>()` once per result set, in order.
- Stored procedures: pass `commandType: CommandType.StoredProcedure`.
- Streaming: `Query<T>(..., buffered: false)` and, on `DbConnection`,
  `QueryUnbufferedAsync<T>` (an `IAsyncEnumerable<T>`).
- `DbString { Value, IsAnsi, IsFixedLength, Length }` sends a `varchar` or
  fixed-length parameter where the default would be `nvarchar`.
- Literal replacement: `{=Name}` inlines a bool or numeric value into the SQL
  instead of sending a parameter.

## Idioms & best practices
- Values reach the database only through the `param` object, never through
  string concatenation or interpolation into the SQL text. The driver page
  (`Npgsql.md`) owns the parameterization rule this enforces.
- Use the `CommandDefinition` overloads when a call must be cancellable. A
  transaction alone does not need them: the plain-string overloads take the
  `IDbTransaction` directly.
- Inside a transaction, pass the `IDbTransaction` to every call. Dapper sets
  the command's transaction only from the argument you give it.
- Alias columns in SQL (`select order_id as OrderId`) or turn on
  `MatchNamesWithUnderscores`, so names match the target type.
- Keep SQL text constant and vary only the parameters. Build dynamic `where`
  clauses from fixed fragments with `DynamicParameters` (or `Dapper.SqlBuilder`);
  never paste values in.
- On SQL Server, match parameter type to column type. Upstream says to send
  Unicode parameters to Unicode columns and ANSI parameters (`DbString` with
  `IsAnsi = true`) to `varchar` columns.
- Keep literal replacement for fixed values, such as a constant status code,
  and test it first; live data belongs in parameters.

## General pitfalls
- Dapper maps by matching result column names to member names. The match
  ignores case, but `order_id` does not match `OrderId` unless
  `MatchNamesWithUnderscores` is on.
  A column with no match is skipped without error and its member stays unset.
- `DateOnly`/`TimeOnly` support has been added, disabled and re-enabled across
  2.x releases. Check the release notes of your pin before you rely on native
  mapping of those types.
- `Execute` with a list makes one round trip per element. It is a convenience,
  not a bulk insert.
- Dapper caches information about every distinct SQL string. SQL built on the
  fly with values inside it fills that cache and can cause memory problems.
- A large `in @list` expands to that many parameters, and each list length is a
  new statement for the plan cache. `PadListExpansions` and
  `InListStringSplitCount` exist for this.
- `QueryFirst` / `QuerySingle` throw when no row comes back (and `QuerySingle`
  also throws on more than one); the `OrDefault` forms return the default.

## Testing
- Upstream documents no testing approach of its own. Its README points to the
  repository's test project as the list of examples.
- Dapper sends your SQL to the database as written, so only a real engine
  checks the SQL. Run data-access tests against the same engine as production,
  for example in a container (`Testcontainers.PostgreSql.md`). The API is
  static extension methods on the connection, so a mocking library cannot stub
  it; to test callers without a database, stub your own repository interface.

## Security defaults
- Values passed through `param` are sent as ADO.NET parameters, never as SQL
  text. SQL injection comes back the moment a value is concatenated or
  interpolated into the SQL string.
- Literal replacement (`{=Name}`) inlines values but accepts only bool and
  numeric types.
- Single-character parameter tokens are detected by default
  (`SupportLegacyParameterTokens`). Prefer named `@param` tokens.

## Operational behaviour
- Connection handling: if the connection is closed, Dapper opens it for the
  call and closes it afterwards. An open connection stays open and stays yours
  to close. Connection pooling is the ADO.NET provider's.
- Results are buffered by default: the whole result set is read into a list
  before the call returns. Upstream says this keeps shared locks in the
  database and network time short. Use unbuffered reads when a result is too
  large to hold in memory.
- The per-query metadata cache is a `ConcurrentDictionary`; statements used
  only once are flushed from it routinely.
- Dapper has no retry, no change tracking and no unit of work. Retries,
  timeouts beyond `CommandTimeout`, and transactions belong to the caller and
  the provider.

## Interop
- Works with any ADO.NET provider; the PostgreSQL driver facts are on
  `Npgsql.md`.
- Can run beside EF Core on the same database, for hand-written SQL over EF's
  connection. EF Core's own notes on mixed access are on
  `Microsoft.EntityFrameworkCore.md`.
- `Dapper.SqlBuilder` composes `where` and `order by` fragments with their
  parameters; `Dapper.Rainbow` adds table-level CRUD helpers.

## Major lines

### 1.x line
- Depends on `System.Data.SqlClient`; so do the first 2.x releases.

### 2.x line
- Early in the line the `System.Data.SqlClient` dependency is removed. A
  project that relied on Dapper to bring it in must reference
  `System.Data.SqlClient` or `Microsoft.Data.SqlClient` itself.
- `AsTableValuedParameter` became generic over `IDataRecord` (a rebuild is
  enough). Nullable reference type annotations arrived during the line.
- Later 2.x releases add `QueryUnbufferedAsync` and `GridReader` unbuffered
  reads on `DbConnection`. Release notes moved from the docs site to GitHub
  Releases.

## Upstream docs
- https://github.com/DapperLib/Dapper (the README is the main guide)
- https://dapperlib.dev/ (project site; archived release notes)
- https://github.com/DapperLib/Dapper/releases
- https://www.learndapper.com/ (community-run guide, not official)
- https://www.nuget.org/packages/Dapper
