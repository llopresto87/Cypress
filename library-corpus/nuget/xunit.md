# xunit — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
xUnit.net is a unit-testing framework for C#, F# and Visual Basic on .NET and
.NET Framework. Tests are plain methods marked with attributes. The test class
itself is the per-test fixture: the framework builds a fresh instance for every
test, so richer setup is expressed through fixture and collection types, not
through setup and teardown attributes. The runner parallelizes work across test
collections by default.

Two package lines carry it, and two companion packages ship on their own
version lines:

- `xunit`: the v2 line, now in maintenance mode (critical fixes only).
- `xunit.v3`: the v3 line, where new features land. It is a separate package,
  not a version bump of `xunit`, so moving to it is a migration.
- `xunit.runner.visualstudio`: the VSTest adapter.
- `xunit.analyzers`: the code analyzers for xUnit.net tests.

Licence: Apache-2.0; the project belongs to the .NET Foundation.

## Install, setup and configuration
- v2: `dotnet new xunit` produces a library project that references `xunit`,
  `xunit.runner.visualstudio` and `Microsoft.NET.Test.Sdk`. The last two are
  what let `dotnet test` and IDE test explorers discover and run the tests
  through VSTest; without them, discovery finds nothing.
- v3: `dotnet new install xunit.v3.templates`, then `dotnet new xunit3`. A v3
  test project has `<OutputType>Exe</OutputType>`: it builds a stand-alone
  executable that runs its own tests (`dotnet run`, or the built binary, with
  `-?` for the switches). For `dotnet test`, the project either uses the
  Microsoft Testing Platform (the template default) or adds
  `xunit.runner.visualstudio` and `Microsoft.NET.Test.Sdk` for VSTest. v3
  needs .NET 8 or later, or .NET Framework 4.7.2 or later, and an SDK-style
  project.
- Per-assembly configuration lives in `xunit.runner.json` at the test project
  root, copied to the output (`<Content Include="xunit.runner.json"
  CopyToOutputDirectory="PreserveNewest" />`). Add the schema reference
  `https://xunit.net/schema/current/xunit.runner.schema.json` for editor
  completion. `<AssemblyName>.xunit.runner.json` wins over the plain name, and
  the two files are never merged.
- Settings that matter most, with their defaults:
  - `parallelizeTestCollections` (default `true`): run different collections
    in parallel; `false` runs the assembly serially. In the 4.x releases of
    `xunit.v3` this maps to `parallelMode` (`none`, `collections`, `all`;
    default `collections`), and an explicit `parallelMode` wins.
  - `maxParallelThreads` (default: the number of CPU threads): `-1` or
    `"unlimited"` removes the cap, and a multiplier such as `"2x"` scales it.
  - `parallelAlgorithm` (default `conservative`): starts only as many tests as
    there are threads, which keeps `Timeout` accurate. `aggressive` starts more
    and suits suites that spend most of their time awaiting I/O.
  - `diagnosticMessages` (default `false`) and `longRunningTestSeconds`
    (default `0`, off): hung-test detection only prints when diagnostic
    messages are on.
  - `methodDisplay` (default `classAndMethod`), `failSkips` (default
    `false`), and in v3 `culture` and `failWarns`.
- Assembly attributes set the same defaults in code:
  `[assembly: CollectionBehavior(CollectionBehavior.CollectionPerAssembly)]`
  (default per class), `MaxParallelThreads`, `DisableTestParallelization`.
  In the 4.x releases of `xunit.v3` the parallel settings move to
  `[assembly: Parallelization(...)]`. A runner switch overrides both code and
  configuration file.

## Core API / usage shape
- `[Fact]` marks a parameterless test. `[Theory]` marks a data-driven test, fed
  by `[InlineData]` for literal cases or `[MemberData]` for cases computed from
  a static property or method. `TheoryData<...>` gives typed rows.
- The test class constructor is per-test setup and `IDisposable` is per-test
  teardown. `IAsyncLifetime` adds `InitializeAsync` and `DisposeAsync`, the
  async setup and cleanup that a constructor cannot express.
- `IClassFixture<T>` shares one fixture instance across the tests of one class.
  The framework builds it before the first test of the class, passes it to the
  constructor, and disposes it after the last test.
- `[CollectionDefinition("name")]` on an empty class that implements
  `ICollectionFixture<T>`, plus `[Collection("name")]` on each test class,
  shares one fixture across several classes. The collection definition must be
  in the same assembly as the tests that use it.
- Fixtures cannot depend on other fixtures, and their creation order is not
  controlled. When one needs another, write a class that owns both.
- `ITestOutputHelper`, taken as a constructor argument, writes output that is
  attached to the test result.
- `[Trait("Category", "Slow")]` tags tests for filtering.
- Assertions are static methods on `Assert`: `Equal`, `True`, `Throws`,
  `ThrowsAsync`, `Contains`, `Equivalent`, and so on.

## Idioms & best practices
- Reach for a class or collection fixture only for state that is expensive to
  build (a container, an in-process server, a database). Per-test
  construction is the default, and it keeps tests independent.
- Put tests that share one external resource in the same collection, so the
  framework runs them one after another. Tests in different collections run in
  parallel and race on anything they share.
- Give each `[Theory]` row a distinct behaviour to prove; a row that only
  permutes inputs adds run time and no information.
- Keep unit and integration tests in separate projects, so a run can choose one
  set and the integration infrastructure stays out of the unit tests.
- Return `Task` from async tests. `async void` tests are not supported: v3
  fails them at runtime.

## General pitfalls
- Parallelism is across collections, not within them. By default each test
  class is its own collection, so tests in different classes run at the same
  time. Two classes that touch the same table, file or port will race unless
  they share a collection.
- An assembly fixture (v3) does not change parallelism. Tests in many
  collections use it at the same time, so it must be safe for concurrent use.
- Observed in practice: a `dotnet test --filter` value that matches nothing
  under VSTest runs zero tests and still exits 0, which reads as "all passed".
  Upstream documents the filter syntax, where `=` is an exact match, `~` is
  "contains", and a bare value means `FullyQualifiedName~value`. An exact
  match on a name that is not the fully qualified one matches nothing. Under
  the Microsoft Testing Platform, a run that discovers no tests exits with code
  8. Check the executed-test count, not just the exit code.
- A v3 test that times out is not stopped by force: the framework signals
  `TestContext.Current.CancellationToken`, and the test must observe it.
- v3 attaches console and trace output to a test through an async-local
  context. Output written from a background thread with no test attached is
  dropped without a message.

## Testing
- The framework is the test harness, so "testing" here means testing the test
  setup. Run the suite with `-list` (v3 console runner or test executable) to
  see what is discovered without running it.
- Prove a parallelism assumption by running the suite with
  `parallelizeTestCollections` set to `false` once. A suite that only passes
  serially has a shared-state race.
- The `xunit.analyzers` package flags common misuse, such as theory data
  whose types do not match the method parameters.

## Security defaults
Upstream documents no security surface for the framework: tests run with the
full rights of the process that runs them, and the framework adds no
sandbox.

## Operational behaviour
- Discovery and execution are separate phases. In v2 the runner loads the test
  assembly; in v3 every test project runs in its own process.
- Default parallelism uses one thread per CPU thread, with the conservative
  algorithm. Runners can also run several test assemblies in parallel, which
  is off by default for the MSBuild runner.
- Fixtures are disposed when their scope ends: a class fixture after the class,
  a collection fixture after the collection, an assembly fixture (v3) after the
  run. In v3, an object that implements both `IAsyncDisposable` and
  `IDisposable` gets only `DisposeAsync`.
- Test order inside a collection is randomized. In v3 the order is stable for
  one assembly path, so a run from another directory (a CI agent, say) uses a
  different order. A `<assembly>.uniqueid` file next to the test assembly pins
  it for reproducing an order-dependent failure.

## Interop
- ASP.NET Core integration tests share a `WebApplicationFactory` through a
  class or collection fixture (`Microsoft.AspNetCore.Mvc.Testing.md`).
- Containers and database resets are owned by a fixture and shared per
  collection (`Testcontainers.PostgreSql.md`, `Respawn.md`). Testcontainers
  ships `Testcontainers.Xunit` (v2) and `Testcontainers.XunitV3` (v3) base
  classes for this.
- Mocks and assertion libraries plug in without framework support
  (`NSubstitute.md`, `Shouldly.md`). In v3, an assertion library whose
  exception implements an interface named `IAssertionException` is reported as
  an assertion failure.
- `dotnet test` filters reach xUnit through `FullyQualifiedName`,
  `DisplayName` and trait names (`--filter "Category=Slow"`).

## Major lines

### v2 line (`xunit` 2.x)
- A library project run by an external runner (VSTest adapter, console or
  MSBuild runner). Maintenance mode: no new features.
- `IAsyncLifetime` declares its own `DisposeAsync`. If a class implements both
  it and `IDisposable`, both are called.
- Console, `Debug` and `Trace` output is not captured; use
  `ITestOutputHelper`. `Timeout` on `[Fact]` needs an async test.

### v3 line (`xunit.v3`)
- Package names change (`xunit` to `xunit.v3`, `xunit.assert` to
  `xunit.v3.assert`, runners to `xunit.v3.runner.*`), `xunit.abstractions` is
  removed, and `xunit.runner.visualstudio` must be from its 3.x line or later.
  `ITestOutputHelper` moves to the `Xunit` namespace.
- Test projects are executables (`OutputType` `Exe`); the minimum runtimes
  rise to .NET 8 and .NET Framework 4.7.2.
- `IAsyncLifetime` inherits `IAsyncDisposable`, and only `DisposeAsync` is
  called when both disposal interfaces are present. `async void` tests fail.
- New: `Assert.Skip`/`SkipWhen`/`SkipUnless` and dynamic skip on `[Fact]`,
  `Explicit` tests, `TestContext.Current` (cancellation token, attachments,
  warnings), assembly fixtures, `[Collection<T>]` on .NET 8, `MatrixTheoryData`,
  `TheoryDataRow` with per-row skip, timeout and traits, async `MemberData`,
  opt-in `[assembly: CaptureConsole]` and `[assembly: CaptureTrace]`, a query
  filter language (`-filter "/Assembly/Namespace/Class/Method"`), culture
  override, and native Microsoft Testing Platform support.
- The 4.x releases of the `xunit.v3` packages add parallel mode `all` (tests
  inside one class run in parallel) with per-collection, per-class, per-method
  and per-row opt-outs, and the `[assembly: Parallelization(...)]` attribute.
  Older test assemblies run with `-parallelMode all` treat it as
  `collections`.

## Upstream docs
- Docs: https://xunit.net/
- Shared context (fixtures): https://xunit.net/docs/shared-context
- Parallelism: https://xunit.net/docs/running-tests-in-parallel
- Configuration file: https://xunit.net/docs/config-xunit-runner-json
- v2 to v3 migration: https://xunit.net/docs/getting-started/v3/migration
- `dotnet test` filters: https://learn.microsoft.com/en-us/dotnet/core/testing/selective-unit-tests
- Repo: https://github.com/xunit/xunit
- Packages: https://www.nuget.org/packages/xunit and https://www.nuget.org/packages/xunit.v3
