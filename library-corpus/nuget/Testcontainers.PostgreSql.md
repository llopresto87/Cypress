# Testcontainers.PostgreSql — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`Testcontainers.PostgreSql` is the PostgreSQL module for Testcontainers for
.NET. It starts a disposable, real PostgreSQL instance in a container for the
lifetime of a test run and hands back its connection string. The trade is
deliberate: container startup cost and a Docker dependency, in exchange for
testing against the real engine instead of an in-memory or fake provider whose
behaviour diverges from PostgreSQL on exactly the things integration tests
exist to catch: SQL dialect, constraints, transactions, concurrency, and
provider-specific types. It builds on the core `Testcontainers` package, and
sibling modules (`Testcontainers.RabbitMq`, `Testcontainers.Redis`,
`Testcontainers.MsSql` and others) share the same builder and lifecycle shape.
Licence: MIT.

## Install, setup and configuration
- `dotnet add package Testcontainers.PostgreSql`, plus an ADO.NET provider
  for the tests (`Npgsql.md`).
- It needs a Docker-API-compatible container runtime, local or remote.
  Testcontainers discovers it automatically; override with `DOCKER_HOST`,
  `DOCKER_CONTEXT`, or the matching keys in `~/.testcontainers.properties`.
  The module runs a Linux image, so on a Windows host the runtime must be in
  Linux-container mode (a Windows-engine CI agent cannot run it).
- Settings read from the environment (each also has a properties-file key),
  with their defaults:
  - `TESTCONTAINERS_RYUK_DISABLED` (default `false`): turns off the resource
    reaper that removes leftover containers.
  - `TESTCONTAINERS_RYUK_CONTAINER_PRIVILEGED` (default `true`): the reaper
    runs privileged.
  - `TESTCONTAINERS_HUB_IMAGE_NAME_PREFIX`: prefixes Docker Hub image names,
    for a registry mirror. `TestcontainersSettings.ImageNameSubstitution`
    rewrites image names in code, before the prefix applies.
  - `TESTCONTAINERS_WAIT_STRATEGY_RETRIES` (default unlimited),
    `TESTCONTAINERS_WAIT_STRATEGY_INTERVAL` (default one second) and
    `TESTCONTAINERS_WAIT_STRATEGY_TIMEOUT` (default one hour).
  - `TESTCONTAINERS_HOST_OVERRIDE`: the host that exposes container ports,
    for remote runtimes.
- Module defaults: database, user and password are all `postgres`; container
  port 5432 is bound to a random host port. The module starts the server with
  `fsync=off`, `full_page_writes=off` and `synchronous_commit=off`, trading
  durability for speed.

## Core API / usage shape
- A builder configures the instance: `new PostgreSqlBuilder("postgres:16")`
  takes the image in its constructor; the parameterless constructor and its
  default-image constant are marked obsolete. Older releases use the
  parameterless constructor plus `.WithImage(...)`; it still compiles on
  current releases with an obsolete warning. Further `With...` calls set the
  rest: `WithDatabase`, `WithUsername`, `WithPassword`, `WithEnvironment`,
  `WithResourceMapping` (copy a file such as an init script into the container
  before it starts), `WithCommand`.
- `Build()` returns a `PostgreSqlContainer`. `StartAsync()` starts it,
  `StopAsync()` stops it, and `DisposeAsync()` removes it; a test fixture
  usually owns this lifecycle, not each test.
- `GetConnectionString()` returns an Npgsql connection string for the running
  instance, including its dynamically mapped host port. `Hostname` and
  `GetMappedPublicPort(5432)` give the parts.
- `ExecScriptAsync(sql)` runs a SQL script inside the container through
  `psql`; `ExecAsync(command)` runs any command; `GetLogsAsync()` returns the
  container logs.
- SQL files mapped into `/docker-entrypoint-initdb.d/` run on first start,
  through the image's own entrypoint.
- `.WithNetwork(network)` and `.WithNetworkAliases("db")` put the container
  on a custom network built with `NetworkBuilder`. Another container on that
  network reaches it at the alias and the container port (`db:5432`).
  `GetConnectionString()` is the host-mapped address and is valid for the
  test process only.
- `.WithWaitStrategy(Wait.ForUnixContainer()...)` overrides readiness.
  `.WithCleanUp(true)` hands teardown to the resource reaper, and
  `.WithAutoRemove(true)` removes the container when it stops.
- `.WithSsl(certificate, key[, ca])` turns on TLS. The connection string's
  `SslMode` is then the test's choice; Testcontainers does not set it.

## Idioms & best practices
- Own the container in a shared test fixture, and do not start one per test
  (`xunit.md` owns the collection-fixture mechanism). Isolate tests from each
  other by resetting or namespacing data (transaction rollback, per-test
  schema, or truncation (`Respawn.md`)), and keep the container running.
  `Testcontainers.XunitV3` (or `Testcontainers.Xunit` for v2) offers
  `ContainerFixture` and `DbContainerFixture` base classes for this.
- Let the module assign the host port and read every connection detail off the
  running container at start time; bind and hard-code nothing fixed, so
  parallel runs and CI agents do not collide. The same goes for names: leave
  container, network and volume names to Docker. Use `Hostname`, not
  `localhost`, as the address.
- One exception, observed in practice: a service whose external URL ends up
  inside artefacts may need a fixed host port. An identity provider whose
  issuer URL is written into every token is the usual case. Accept the
  collision risk knowingly and document it beside the fixture. Upstream's
  best practices say only to avoid static port bindings.
- Pin the image tag explicitly, even with a module builder.
- Copy files in with `WithResourceMapping`; avoid bind-mounting host paths,
  which differ between machines and CI.

## General pitfalls
- It requires a running Docker daemon on the test host. Tests pass locally and
  fail in CI whenever the pipeline has no daemon provisioned. Observed in
  practice: the failure can surface as an opaque connection error from the
  fixture, failing every test in the collection, so it does not read as
  "Docker missing". The library itself throws `DockerUnavailableException`
  when it cannot reach the Docker endpoint; check the first fixture error,
  not the per-test ones.
- Container startup dominates first-test latency, and the cost is paid per
  container started, which is what turns a per-test container into a slow
  suite.
- The image passed to the builder decides which server version the suite
  witnesses. An exact minor pinned here while deployment floats on a moving tag
  means a green suite is evidence about a version that is not deployed. Keep
  the test image and the deployed image on the same version line; the rule is
  owned by `../container/postgres.md`.
- A custom wait strategy replaces the module's own readiness check. By
  default the module runs `pg_isready` against `localhost` inside the
  container, which only passes once init scripts have run and the server
  listens on TCP. A log-message wait added by hand takes that check away.
- The default wait timeout is one hour. A container that never becomes ready
  holds a CI job for that long; pass a timeout in the wait strategy options
  (`o => o.WithTimeout(...)`) or a `CancellationToken` to `StartAsync`.
- Durability is off in the module's defaults, so tests of crash recovery or
  fsync behaviour do not test what production does.
- On CI services that cannot run the reaper container, it must be disabled
  with `TESTCONTAINERS_RYUK_DISABLED=true`, and something else must clean
  up containers.

## Testing
- This module is a test dependency. Smoke-test the fixture itself with one
  test that opens a connection and runs `SELECT 1`
  (`ExecScriptAsync("SELECT 1;")` must return exit code 0), so a broken
  environment fails one obvious test first.
- `GetLogsAsync()` after a failure, or `WithOutputConsumer(...)` while it
  runs, shows what the server said.

## Security defaults
- The default credentials are `postgres`/`postgres`, and the port is
  published on the Docker host. Treat the container as throwaway test
  infrastructure, never as a shared database.
- The resource reaper runs privileged by default and talks to the Docker
  socket. Anything with access to the Docker socket controls the host; on a
  shared CI runner, that is a host-level trust decision
  ([docker-host-hardening.md](../container/docker-host-hardening.md) owns the
  socket trust model).
- The reaper image is pinned by digest. A private registry must mirror it
  with the full multi-platform manifest (or set
  `TESTCONTAINERS_RYUK_CONTAINER_IMAGE`).

## Operational behaviour
- The first container start in a process also starts the reaper (Ryuk). The
  reaper removes the session's containers, networks and volumes after the test
  process ends, whether the tests passed or not.
- Image pull is part of the first start; a cold CI agent pays it per image.
- Starting can be cancelled with a `CancellationToken`. A container that exits
  during startup raises `ContainerNotRunningException` with its exit code and
  logs.
- Testcontainers logs to the console by default; pass `WithLogger(ILogger)`
  to route it through the test framework.

## Interop
- Npgsql consumes the connection string (`Npgsql.md`); EF Core uses it
  through its Npgsql provider (`Microsoft.EntityFrameworkCore.md`).
- Respawn resets data between tests on the same container (`Respawn.md`).
- ASP.NET Core integration tests pass the connection string into the app
  under test through test configuration
  (`Microsoft.AspNetCore.Mvc.Testing.md`).
- xUnit fixtures own the lifecycle (`xunit.md`).

## Major lines
Upstream publishes no per-major-line comparison of this module's surface.
This page follows the current builder source: the image goes in the
constructor, and the parameterless constructor (with `WithImage(...)`) is
marked obsolete. Older releases use `new PostgreSqlBuilder().WithImage(...)`.

## Upstream docs
- Module: https://dotnet.testcontainers.org/modules/postgres/
- Docs: https://dotnet.testcontainers.org/
- Best practices: https://dotnet.testcontainers.org/api/best_practices/
- Wait strategies: https://dotnet.testcontainers.org/api/wait_strategies/
- Configuration: https://dotnet.testcontainers.org/custom_configuration/
- Repo: https://github.com/testcontainers/testcontainers-dotnet
- Package: https://www.nuget.org/packages/Testcontainers.PostgreSql
