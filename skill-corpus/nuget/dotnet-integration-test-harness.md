---
name: dotnet-integration-test-harness
description: Build an ASP.NET Core integration-test harness that boots the real application against real dependencies in containers, once per test collection, and isolates each test with a data reset and re-seed. Invoke when a .NET service needs integration tests through its full HTTP pipeline, or when an existing harness is slow, flaky, or leaks state between tests.
id: skill.dotnet-integration-test-harness
tier: 2
kind: skill
title: dotnet-integration-test-harness, one collection fixture, real containers, a reset per test
owns:
  - dotnet-integration-test-harness.fixture-shape
  - dotnet-integration-test-harness.configuration-entry
  - dotnet-integration-test-harness.reset-discipline
requires:
load_when:
  - "integration tests for an asp.net core service with testcontainers"
  - "share one webapplicationfactory and its containers across test classes"
  - "reset the test database between tests, respawn"
  - "integration tests leak state, are slow, or race each other"
stack:
  - library-corpus/nuget/Microsoft.AspNetCore.Mvc.Testing
  - library-corpus/nuget/Testcontainers.PostgreSql
  - library-corpus/nuget/Respawn
  - library-corpus/nuget/xunit
est_tokens: 1887
---

# Suggested skill: dotnet-integration-test-harness

> Optional procedure, **stack-keyed** on .NET: the harness that runs a
> service's integration tests through its real HTTP pipeline, against real
> dependencies started in containers, paying the startup cost once and
> keeping tests independent with a data reset. **Composes**
> `protocols/test-first.md` (the harness is where RED integration tests run),
> `protocols/verify.md` (count what ran) and the library pages it is built
> from, by reference: `library-corpus/nuget/xunit.md` (fixtures and
> collections), `library-corpus/nuget/Microsoft.AspNetCore.Mvc.Testing.md`
> (the in-process host and its configuration entry points),
> `library-corpus/nuget/Testcontainers.PostgreSql.md` (containers and
> networks) and `library-corpus/nuget/Respawn.md` (the reset). It adds the
> shape that joins them and the order of each step.

**Instantiate by supplying:** `<PROGRAM>` (the application's entry type),
`<DEPENDENCIES>` (each external system the application needs at startup: the
database, an identity provider, a broker, an HTTP dependency to fake),
`<SETTINGS>` (the configuration keys that point the application at each of
them), `<REFERENCE_DATA>` (the rows every test expects to exist) and
`<IGNORED_TABLES>` (tables the reset must leave alone).

## When to apply

- A service needs integration tests that go through routing, authentication,
  validation and persistence together.
- An existing integration suite starts containers per test class or per test
  and is slow, or tests pass alone and fail together.

## 1. One fixture owns the whole harness

*Replaces: a fixture per test class, each starting its own containers.*

- Write one fixture class that derives from
  `WebApplicationFactory<<PROGRAM>>` and implements `IAsyncLifetime`. It owns
  every container, the network they share, the respawner and the seeder.
  Fixtures cannot depend on other fixtures in xUnit, so one class owning all
  of it is the shape, not a convenience.
- Share it through a **collection**: an empty class marked
  `[CollectionDefinition("<name>")]` that implements
  `ICollectionFixture<TheFixture>`, and `[Collection("<name>")]` on every
  integration test class. The definition must live in the test assembly.
  Tests inside one collection run one after another, which the shared
  database requires (a reset takes table locks that parallel tests would
  wait on or fail against: `library-corpus/nuget/Respawn.md`, Operational
  behaviour).
- **Gate:** the containers start once per run (the test output or the
  container runtime's listing shows one set), not once per class.

## 2. Start the dependencies in `InitializeAsync`

- Create one network with `NetworkBuilder`, and start each container in
  `<DEPENDENCIES>` on it with a network alias, so containers reach each other
  by alias and the application, which runs in the test process, reaches each
  through its mapped host port and the container's connection string.
- **The exception is an identity provider** whose issuer URL is written into
  every token: the issuer must stay stable, so bind that container's port on
  purpose (`library-corpus/nuget/Testcontainers.PostgreSql.md`, Idioms). To
  relax `JwtBearerOptions` in tests, use named `Configure`, not
  `PostConfigure` (`library-corpus/nuget/Microsoft.AspNetCore.Mvc.Testing.md`,
  Idioms & best practices).
- Wait for readiness with the container's wait strategy, not with a delay.
- Fake an HTTP dependency at its transport seam (a stub server the
  configuration points at), and keep the rest of the pipeline real.
- `DisposeAsync` stops and removes what `InitializeAsync` started; the
  library's reaper removes leftovers after a crashed run.

## 3. Hand the application its settings through the right entry point

*Replaces: assuming `ConfigureAppConfiguration` reaches every reader.*

The factory offers several configuration entry points, and they differ in
when the application can see the values
(`library-corpus/nuget/Microsoft.AspNetCore.Mvc.Testing.md`, Install, setup
and configuration):

- `ConfigureWebHost` with `builder.ConfigureAppConfiguration(c => c.AddInMemoryCollection(<SETTINGS>))`
  is visible only after `WebApplicationBuilder.Build()`. A value that
  `Program.cs` reads from `builder.Configuration` **before** `Build()` (to
  choose a provider, register a client, size a pool) does not see it, and the
  application starts against its default.
- For values read before `Build()`, override `CreateHost` and set them with
  `builder.ConfigureHostConfiguration(...)` (this needs `Program.cs` to pass
  `args` to `WebApplication.CreateBuilder`), or set environment variables
  before the factory starts the host.
- Replace a registration (the database context pointed at the container, an
  authentication option) in `ConfigureServices` or `ConfigureTestServices`,
  which run after the application's own registrations.
- Services that validate their configuration at startup still need their
  settings even when a test fakes the service that consumes them, and every
  hosted background service starts with the host
  (`library-corpus/nuget/Microsoft.AspNetCore.Mvc.Testing.md`, General
  pitfalls).
- **Gate:** a test that reads each `<SETTINGS>` value back from the running
  application (or from the resolved options) and asserts it names the
  container, not a default host.

## 4. Build the respawner once; reset and re-seed per test

- The respawner needs the schema in place. The factory builds the host
  lazily, so force the first host start inside `InitializeAsync` by touching
  `Services` (or calling `CreateClient()`) after the containers are up. That
  applies the migrations only when the application migrates at startup;
  otherwise the fixture applies them itself first, because `CreateAsync`
  throws when it finds no tables (`library-corpus/nuget/Respawn.md`). Then open
  a connection to the container database and create the respawner once:
  `Respawner.CreateAsync(connection, new RespawnerOptions { DbAdapter = DbAdapter.Postgres, SchemasToInclude = [...], TablesToIgnore = [<IGNORED_TABLES>, the migrations history table] })`.
  Set `DbAdapter` explicitly: older major lines default to SQL Server and
  later ones infer it from the connection (`library-corpus/nuget/Respawn.md`,
  Major lines).
- Before each test (the test class's `InitializeAsync`, or a fixture method
  each test calls first), run `ResetAsync(connection)` and then re-seed
  `<REFERENCE_DATA>`. The reset is the cheap step; the creation reads
  metadata and is not repeated.
- **Choose per table: ignore or re-seed.** A table in `TablesToIgnore` keeps
  its rows across tests, so tests that write to it must use unique keys. A
  reference table that is reset must be re-seeded after every reset; dropping
  that re-seed breaks dependent tests later, with nothing pointing back at
  the reset. Whoever adds a reference table updates the ignore list or the
  seeder in the same change.
- Rebuild the respawner if a test run creates tables after `CreateAsync`.
- **Never point the respawner at shared configuration.** It deletes every
  row it can reach; build its connection only from the container.
- **Gate:** a guard test that, right after a reset and re-seed, asserts each
  reference table has its rows and each data table is empty.

## 5. Write the tests

- Each test takes the fixture through its constructor, creates its own
  `HttpClient` with `CreateClient()`, and asserts through HTTP responses and,
  where the behavior is persistence, through a read of the database.
- A test that needs different settings (a low rate limit, a feature flag)
  derives a factory with `WithWebHostBuilder(...)` for that test only.
- **Gate:** run the suite and check the number of tests executed, not only
  the exit code: a filter that matches nothing runs zero tests and still
  exits successfully (`library-corpus/nuget/xunit.md`).

## Failure table

| symptom | cause | step |
|---|---|---|
| the application connects to a default or local host instead of the container | a value read before `Build()` was supplied through `ConfigureAppConfiguration` | 3 |
| the host fails to build in a test that fakes a service | that service's startup configuration is absent | 3 |
| tests pass alone and fail in a full run | state left by an earlier test: a table neither reset nor written with unique keys, or reference data lost to a reset | 4 |
| the reset fails and nothing is reset | a table guarded against deletion is in scope | 4, add it to `TablesToIgnore` |
| a suite is slow and the container runtime shows many short-lived containers | containers started per class or per test | 1 |
| tests time out waiting on each other | parallel collections sharing one database | 1 |

## Reference files

- `library-corpus/nuget/xunit.md`
- `library-corpus/nuget/Microsoft.AspNetCore.Mvc.Testing.md`
- `library-corpus/nuget/Testcontainers.PostgreSql.md`
- `library-corpus/nuget/Respawn.md`
- `protocols/test-first.md`, `protocols/verify.md`
