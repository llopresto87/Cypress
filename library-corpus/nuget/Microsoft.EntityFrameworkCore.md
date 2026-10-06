# Microsoft.EntityFrameworkCore — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
.NET's core object-relational mapper. A `DbContext` exposes `DbSet<T>`
properties, tracks changes to the entities it materializes, translates LINQ
queries into SQL through a database provider, and persists tracked changes on
`SaveChanges`. Model shape is declared through a fluent configuration surface
(with attribute-based configuration as an alternative), and schema evolution is
expressed as migrations generated from that model. An application normally
installs a provider package, which brings the core package with it:

- `Microsoft.EntityFrameworkCore`: the core package.
- `Microsoft.EntityFrameworkCore.SqlServer`: the SQL Server provider.
- `Microsoft.EntityFrameworkCore.Sqlite`: the SQLite provider.
- `Npgsql.EntityFrameworkCore.PostgreSQL`: a third-party provider, for
  PostgreSQL.

Licence: MIT. EF Core releases follow the .NET
release and support schedule; each major line has a stated end of support.

## Install, setup and configuration
- Install the provider package: `dotnet add package
  Microsoft.EntityFrameworkCore.SqlServer` (or the provider you use).
- Design-time tooling needs `Microsoft.EntityFrameworkCore.Design` in the
  project the tools build, plus the `dotnet-ef` tool, installed globally
  (`dotnet tool install --global dotnet-ef`) or as a local tool in a tool
  manifest beside the solution. Visual Studio's Package Manager Console uses
  `Microsoft.EntityFrameworkCore.Tools` instead.
- Keep the tools package, `.Design`, the core package and the provider on the
  same major. The docs require the tools to match the runtime packages' major,
  and providers do not work across majors: a provider built for one major
  fails with the next.
- Register the context in DI with `services.AddDbContext<TContext>(o =>
  o.UseSqlServer(connString))`. This registers it as **scoped**, so each web
  request gets its own instance. The context class needs a public constructor
  that takes `DbContextOptions<TContext>`.
- `AddDbContextFactory<TContext>` registers an `IDbContextFactory<TContext>`
  for code that needs several units of work in one scope, or a context outside
  a request (background services, Blazor Server).
- `AddDbContextPool<TContext>` reuses context instances: on dispose, EF resets
  the instance and returns it to a pool (`poolSize` defaults to 1024; past that
  it creates instances on demand). It is separate from the driver's
  connection pool.
- Options on `DbContextOptionsBuilder` that change behaviour:
  `UseQueryTrackingBehavior` (default tracking for queries), `LogTo` /
  `UseLoggerFactory`, `EnableSensitiveDataLogging` (puts data values in logs
  and exceptions; off by default), `EnableDetailedErrors`,
  `ConfigureWarnings` (ignore, log or throw per event id), `AddInterceptors`.
- Provider options carry `MigrationsAssembly(...)` when migrations live in a
  different assembly from the context, and `EnableRetryOnFailure()` for the
  provider's retrying execution strategy (see Operational behaviour).

## Core API / usage shape
- `IEntityTypeConfiguration<T>` puts each entity's mapping in its own class;
  `modelBuilder.ApplyConfigurationsFromAssembly(...)` discovers them, keeping
  `OnModelCreating` from becoming a monolith.
- Query with LINQ over a `DbSet<T>` and finish with an async operator
  (`ToListAsync`, `FirstOrDefaultAsync`, `SingleAsync`). `Include` /
  `ThenInclude` load related data eagerly; `Select` projects to the shape a
  caller needs.
- `AsNoTracking()` on read-only query paths skips change-tracker bookkeeping,
  the default choice for queries whose results are never saved back.
- `AsSplitQuery()` loads each included collection with its own SQL statement
  instead of one JOIN.
- `SaveChanges` / `SaveChangesAsync` writes every tracked change in one
  transaction.
- `ExecuteUpdateAsync` / `ExecuteDeleteAsync` issue set-based UPDATE/DELETE
  statements directly, without materializing entities or round-tripping them
  through the change tracker.
- Raw SQL: `FromSql($"...")` on a `DbSet` (entity results) and
  `Database.SqlQuery<T>($"...")` (scalar or unmapped results) take an
  interpolated string and turn each hole into a `DbParameter`.
  `FromSqlRaw` / `ExecuteSqlRaw` take a plain string and parameters you pass
  separately.
- `HasConversion(...)` maps a value object or domain-typed property to a
  primitive column, keeping the domain type out of the storage shape.
- Optimistic concurrency: mark a property with `[Timestamp]` (a database row
  version) or `IsConcurrencyToken()`. When the row changed underneath, the
  update matches no rows and `SaveChanges` throws
  `DbUpdateConcurrencyException`, which the application must catch and resolve.
- Interceptors: `ISaveChangesInterceptor` (or the `SaveChangesInterceptor`
  base class) runs around `SaveChanges`; `DbCommandInterceptor` and
  `DbConnectionInterceptor` wrap commands and connections. Register them with
  `AddInterceptors(...)`. To resolve an interceptor from DI, use the
  `AddDbContext<TContext>((sp, o) => o.AddInterceptors(sp.GetRequiredService<...>()))`
  overload.
- The migrations CLI (`dotnet ef`, the `dotnet-ef` tool) needs two projects.
  `--project` names the one that holds the migrations and references
  `Microsoft.EntityFrameworkCore.Design`/`.Tools`; `--startup-project` names the
  one the tool builds and runs to obtain a configured `DbContext`. In a layered
  solution they differ, and the CLI's guess from the current directory is
  usually wrong:
  `dotnet ef migrations add <Name> --project <data-project> --startup-project <host-project>`.
  At run time, `MigrationsAssembly(...)` on the provider options is the
  counterpart of `--project`: it tells EF which assembly holds the migrations.
  An application that applies or discovers migrations at run time also needs a
  normal project reference to that assembly.
- A migration is emitted as a timestamp-prefixed file whose class name carries
  no timestamp. Name it verb-first in PascalCase (`AddOrderStatus`); the tool
  adds the timestamp to the file name only.
- Migrations can be applied four ways: a generated SQL script (`dotnet ef
  migrations script --idempotent --output <file>`), a migrations bundle
  (`dotnet ef migrations bundle`, a single executable that needs neither the SDK
  nor the source), `dotnet ef database update`, or `Database.MigrateAsync()` at
  run time. `dotnet ef migrations has-pending-model-changes` reports whether
  the model has moved past the last migration.

## Idioms & best practices
- Treat the `DbContext` as a short-lived unit of work, scoped to a request or
  operation, rather than a long-lived shared object.
- Prefer explicit projection to the shape a caller needs over loading
  full entity graphs and discarding most of them.
- Choose eager loading or projection over lazy loading. Lazy loading in a loop
  issues one query per parent row (the N+1 problem).
- Keep migrations generated from the model and reviewed as code, so the schema
  history stays a readable record rather than an opaque artifact. Read every
  generated migration before it runs: a rename can come out as a drop and an
  add.
- For automated deployment the docs recommend a migrations bundle. Use an
  idempotent SQL script when the SQL must be reviewed or handed to a DBA.
  `dotnet ef database update` is for local development.
- Run `dotnet ef migrations has-pending-model-changes` in CI, so a model change
  without its migration fails the build instead of the deploy.
- Apply migrations with a deployment identity that may change the schema, and
  run the application with an identity that can only read and write data.
- Record the exact `dotnet ef` invocation for the solution (both project flags
  and any environment the host needs) in the project's runbook the first time
  it is worked out, so nobody re-derives it.
- Keep audit fields (created/modified by and at) out of call sites with a
  `SaveChangesInterceptor` resolved from DI. Observed in practice: such an
  interceptor needs the acting user, so it needs a current-user abstraction that
  also works outside an HTTP request (background jobs, tests, seeding). The
  interceptor docs do not cover this.

## General pitfalls
- EF Core can warn that the model has changes not yet captured in a migration
  (`PendingModelChangesWarning`). Suppressing that warning to make a build or
  test run green lets model and schema diverge silently, and the drift ships to
  production undetected. Fix the migration instead of silencing the warning.
  The docs list one legitimate case for suppressing it: migrations generated or
  chosen dynamically by replaced EF services.
- A model built non-deterministically (`DateTime.Now`, `Guid.NewGuid()` in
  `HasData`) looks changed on every build and raises the same warning. Use
  static seed values.
- `Database.Migrate()` at startup runs whatever migrations merged, on the first
  boot after deploy, with no review gate in between; the general rule lives in
  `../container/postgres.md`. It also needs schema-changing rights for the
  application's own identity.
- Do not call `EnsureCreated()` before `Migrate()`: it creates the schema
  without migrations, and the later `Migrate()` fails.
- A `DbContext` does not support parallel operations. Two queries in flight on
  one instance throw `InvalidOperationException` ("A second operation started
  on this context..."). Await each call before the next, or use separate
  instances.
- `ExecuteUpdate` and `ExecuteDelete` do not start a transaction, and they do
  not update entities already tracked in the context. Wrap several of them in
  an explicit transaction when they must succeed together.
- With the retrying execution strategy enabled, a transaction you open yourself
  throws ("does not support user-initiated transactions"). Run the whole
  transaction inside `Database.CreateExecutionStrategy().ExecuteAsync(...)` so
  it retries as one unit.
- Several collection `Include`s at the same level in one query multiply rows
  (cartesian explosion). Split queries avoid that, but they are separate round
  trips with no consistency guarantee between them unless you wrap them in a
  serializable or snapshot transaction.
- `FromSqlRaw` and `ExecuteSqlRaw` with a concatenated or interpolated
  `string` are open to SQL injection. Keep user values in parameters.
- `dotnet-ef` is usually a global tool, and a global tool built for a newer .NET
  major than the target fails to start where only the target's runtime is
  installed (or the reverse). The runtime roll-forward variable fixes it; that
  fact is owned by `../language/dotnet.md`. A local tool manifest pinned beside
  the solution avoids the mismatch.
- `EnableSensitiveDataLogging()` puts entity and parameter values into logs and
  exception messages. It is a local debugging aid; keep it out of every deployed
  configuration.
- A singleton interceptor (one that implements `ISingletonInterceptor`) built
  as a new instance each time a context is configured makes EF build a new
  internal service provider each time. EF raises
  `ManyServiceProvidersCreatedWarning` and slows down. Reuse one instance.

## Testing
- The EF team recommends testing against the production database engine.
  Containers (for example through Testcontainers) make a real engine cheap to
  start, and the docs say a local real database is usually fast enough.
- The InMemory provider is discouraged for testing and gets no new features.
  It is not relational: constraints, transactions, raw SQL and
  provider-specific types and translations behave differently or not at all.
  Observed in practice, and in line with the docs: integration tests that run
  the real migrations against the real engine caught defects the InMemory
  provider hid.
- SQLite in-memory as a stand-in for another engine also diverges: providers
  translate queries differently.
- Mocking `DbSet` query behaviour is not possible, because LINQ operators are
  static extension methods. A "mocked" set is really an in-memory collection and
  has the InMemory provider's problems. To test without a database, put a
  repository layer between the application and EF Core and stub that.
- Mocking `DbContext` does work for checking write calls (`Add`,
  `SaveChanges`).
- Isolate tests that share a real database: reset data between tests (for
  example with Respawn, see `Respawn.md`) or run each test in a transaction
  that is rolled back.

## Security defaults
- EF does not put data values in exception messages or logs by default.
  `EnableSensitiveDataLogging()` turns that off.
- LINQ queries, `FromSql`, `FromSqlInterpolated` and `SqlQuery` send values
  as parameters. `FromSqlRaw` and `ExecuteSqlRaw` are safe only when values
  are passed as separate parameters, never concatenated into the string.
- Keep production connection strings out of source control and out of a
  migrations bundle; pass the deployment connection from a secret store
  (`efbundle --connection ...`). A bundle reads `appsettings.json` from its own
  directory, so keep secrets out of files shipped beside it.
- Design-time tools run application code and default to the `Development`
  environment when neither `ASPNETCORE_ENVIRONMENT` nor `DOTNET_ENVIRONMENT`
  is set. Set the environment explicitly when you build or run a bundle, or it
  may load development settings or user secrets.

## Operational behaviour
- Creating a context is cheap and does no database work. The connection opens
  per operation and returns to the driver's pool right after, unless you open
  it yourself or a transaction holds it.
- Query compilation is cached by query shape, so a repeated query with
  different parameter values reuses its plan. Building queries whose shape
  changes each time (inlined constants, dynamic expression trees) defeats the
  cache. `EF.CompileAsyncQuery` removes the remaining lookup cost on hot paths.
- `ToListAsync` and similar operators buffer all results in memory;
  `AsAsyncEnumerable` streams them. Enabling the retrying execution strategy
  buffers results internally, which raises memory use for large result sets.
- Transient failures: `EnableRetryOnFailure()` turns on the provider's
  retrying execution strategy, where each query and each `SaveChanges` is
  retried as a unit.
- Migration locking (9.x and later): `Migrate`, `MigrateAsync`,
  `dotnet ef database update` and bundles take a database-wide lock before they
  apply migrations, so several instances migrating at once do not corrupt the
  schema. SQL scripts are not covered by the lock. On SQLite the lock is a table
  that can stay behind if the process dies, blocking later migrations.
- Bundles and containers: build the bundle in CI and run it as a one-shot job
  after the database is healthy. The docs advise against installing the SDK or
  running `dotnet ef` in the application image, and against migrating from
  every replica's entrypoint.
- Rolling back: `efbundle <Migration>` or `dotnet ef database update
  <Migration>` runs the `Down` methods of every newer migration; `0` reverts
  everything. That can lose data.

## Interop
- PostgreSQL goes through `Npgsql.EntityFrameworkCore.PostgreSQL`, which the
  Npgsql project maintains on its own release schedule. Check that it supports
  the EF major you are moving to before you upgrade. The driver facts are on
  `Npgsql.md`.
- Dapper can run on the same connection for hand-written SQL. On SQL Server,
  from the 10.x line EF injects an `Application Name` into a connection string
  that lacks one, so EF and another data access path get different connection
  pools. Inside a `TransactionScope` that can escalate to a distributed
  transaction. Setting `Application Name` yourself stops the injection.
- ASP.NET Core Identity's EF stores
  (`Microsoft.AspNetCore.Identity.EntityFrameworkCore`) add tables to your
  model. Options that change the Identity schema must be visible to the design
  time tools, so run them with the application as startup project or provide an
  `IDesignTimeDbContextFactory`.
- Test infrastructure: `Testcontainers.PostgreSql.md`, `Respawn.md`, and
  `Microsoft.AspNetCore.Mvc.Testing.md` for swapping the context registration
  in a test host.

## Major lines

### 8.x line
- Targets .NET 8.
- A parameterized collection in `Contains` is sent as one JSON array parameter
  (`OPENJSON` on SQL Server). That SQL fails on SQL Server 2014 and older, or a
  newer server set to an old compatibility level.
- Enums inside JSON columns are stored as integers by default.
- Scaffolding maps SQL Server `date` and `time` to `DateOnly` and `TimeOnly`.
- `dotnet ef migrations has-pending-model-changes` arrives in this line.

### 9.x line
- Targets .NET 8, so a .NET 8 application can take it.
- `Migrate`, `MigrateAsync` and `dotnet ef database update` throw when the
  model has pending changes (`PendingModelChangesWarning`).
- Migrating inside a transaction you opened yourself throws
  (`MigrationsUserTransactionWarning`): EF now manages the transaction and the
  execution strategy, and takes the migration lock. Remove the outer
  transaction.
- All pending migrations run in one transaction. The 10.x line goes back to
  one transaction per migration.
- With newer .NET SDKs the tools can fail to find
  `Microsoft.EntityFrameworkCore.Design`. The documented workaround adds
  `<Publish>true</Publish>` to that package reference; the 10.x line fixes it.
- EF tools drop support for .NET Framework projects. `UseSeeding` and
  `UseAsyncSeeding` are the seeding hooks the migration paths run.

### 10.x line
- Targets .NET 10.
- On a project with several target frameworks, the EF tools need
  `--framework <tfm>`.
- A parameterized collection in `Contains` becomes several scalar parameters by
  default. `UseParameterizedCollectionMode(...)` or the per-query `EF.Constant`,
  `EF.Parameter` and `EF.MultipleParameters` restore other translations.
- `ExecuteUpdate` takes a plain lambda for its setters instead of an expression
  tree; code that built the tree by hand fails to compile.
- SQL Server: `UseAzureSql`, or compatibility level 170 and above, maps JSON
  columns to the `json` type, and the next migration converts existing
  `nvarchar(max)` JSON columns.

## Upstream docs
- https://learn.microsoft.com/en-us/ef/core/
- https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/
- https://learn.microsoft.com/en-us/ef/core/testing/choosing-a-testing-strategy
- https://learn.microsoft.com/en-us/ef/core/cli/dotnet
- https://learn.microsoft.com/en-us/ef/core/managing-schemas/migrations/applying
- https://learn.microsoft.com/en-us/ef/core/what-is-new/ (releases, support and
  the breaking-changes page of each major line)
- https://github.com/dotnet/efcore
- https://www.nuget.org/packages/Microsoft.EntityFrameworkCore
