# Microsoft.AspNetCore.Mvc.Testing — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`Microsoft.AspNetCore.Mvc.Testing` is the official integration-testing host for
ASP.NET Core apps built with MVC, Razor Pages or Minimal APIs. It provides
`WebApplicationFactory<TEntryPoint>`, which boots the **real application
in-process** on a `TestServer` (from `Microsoft.AspNetCore.TestHost`, pulled in
as a dependency): real routing, real middleware, real model binding, real DI.
Tests then substitute individual services at the seams. The point is a real
pipeline with a few chosen boundaries faked, not a mocked imitation of one.
The package also copies the app's `.deps.json` into the test output and sets
the content root to the app's project folder, so views and static files are
found. Licence: MIT; it ships from the `dotnet/aspnetcore` repository.

## Install, setup and configuration
- Reference the package from a separate test project that uses the Web SDK
  (`<Project Sdk="Microsoft.NET.Sdk.Web">`) and references the app project.
  With xUnit and the VSTest adapter, also reference `Microsoft.NET.Test.Sdk`.
- Each major line of the package targets the matching .NET line (the 10.x
  package targets `net10.0`), so keep it on the same major line as the
  ASP.NET Core runtime under test.
- With top-level statements the compiler makes `Program` internal. Expose it
  either with `<InternalsVisibleTo Include="MyApp.Tests" />` in the app
  project, or by adding `public partial class Program { }` at the end of
  `Program.cs`.
- The app under test runs in the `Development` environment unless the
  factory sets another one (`builder.UseEnvironment("Testing")` inside
  `ConfigureWebHost`).
- The factory finds the content root through a
  `WebApplicationFactoryContentRootAttribute` on the test assembly, keyed by
  the entry assembly's full name. Without one it looks for a solution file
  (`.sln`) and appends the entry assembly name to that folder.
- Test configuration has three entry points, and they differ in when the
  values become visible:
  - `ConfigureWebHost` plus `builder.ConfigureAppConfiguration(c =>
    c.AddInMemoryCollection(...))`: the source is kept, but it is only visible
    after `WebApplicationBuilder.Build()`. Code in `Program.cs` that reads
    `builder.Configuration[...]` before `Build()` does not see these values.
  - Override `CreateHost(IHostBuilder)` and call
    `builder.ConfigureHostConfiguration(...)`: the values are enumerated
    before the entry point runs and passed in through `args`, so they are
    visible before `Build()`. This only works when `Program.cs` passes `args`
    to `WebApplication.CreateBuilder(args)`.
  - Environment variables set before the factory starts the host (for
    example `ASPNETCORE_ENVIRONMENT`), which the host reads as usual.

## Core API / usage shape
- Subclass `WebApplicationFactory<TEntryPoint>` and override
  `ConfigureWebHost(IWebHostBuilder builder)` to reach the host builder from a
  test fixture.
- `builder.ConfigureServices(...)` inside the factory runs **after** the app's
  own registrations in `Program.cs`. Remove a registration by finding its
  `ServiceDescriptor` and calling `services.Remove(...)`, then add the
  replacement.
- `builder.ConfigureTestServices(...)` is the substitution point for test
  doubles; it also runs after the app's registrations, so a service replaced
  there wins over what `Program.cs` registered.
- `factory.CreateClient()` returns an `HttpClient` wired to the in-process
  server; requests go through the full pipeline without a network listener
  or a port. The default client follows redirects and handles cookies. Pass
  `WebApplicationFactoryClientOptions` to change that (`AllowAutoRedirect`,
  `HandleCookies`, `BaseAddress`, `MaxAutomaticRedirections`).
- `factory.WithWebHostBuilder(b => ...)` derives a new factory with extra
  configuration, typically one `ConfigureTestServices` override for one test,
  without touching the shared factory. The parent factory disposes the
  factories derived from it.
- `factory.Services` is the app's root service provider. Resolve scoped
  services through `factory.Services.CreateScope()`, for example to seed a
  database before a request.
- To test authorization without a real identity provider, register a
  test-only, header-driven `AuthenticationHandler<AuthenticationSchemeOptions>`
  in `ConfigureTestServices`, so each request picks its user and claims
  through a request header (the docs' example sends `Authorization: Test`) (`services.AddAuthentication("TestScheme")
  .AddScheme<AuthenticationSchemeOptions, TestAuthHandler>("TestScheme", _ =>
  { })`) and make it the default authenticate and challenge scheme. The
  scheme name must match the scheme the app's policies expect, or
  authentication silently does not apply.

## Idioms & best practices
- Own the factory in a shared test fixture and create a fresh client per
  test; the factory is expensive to build and safe to share (`xunit.md` owns
  the fixture mechanism).
- Swap one specific boundary per concern (an outbound HTTP client, a clock, a
  message broker), not a whole subsystem.
- Substitute at an owned abstraction (the app's own interface for an external
  system) before intercepting transport, so the test names the boundary it is
  faking.
- Keep the real pipeline intact: every piece of middleware removed to make a
  test pass is a piece of production behaviour the test stops covering.
- Set the environment explicitly in the factory, so the tests do not depend
  on whatever `Development` turns on in the app.
- Set `AllowAutoRedirect = false` when the assertion is about the first
  response (a redirect to a login page, a `Location` header), not the page
  the redirect ends on.
- An alternative to a fake authentication handler, observed in practice: run
  a real identity provider in a container and point the app's JWT bearer
  options at it, so the real token pipeline runs in the tests. The cost is
  that the provider's issuer URL ends up inside every token, which usually
  forces a fixed host port for that container. Upstream describes containers
  with access tokens as one way to test secured APIs and does not discuss the
  port trade-off.
- To relax `JwtBearerOptions` in tests (a non-HTTPS metadata address, say),
  use named `Configure`, not `PostConfigure`;
  `Microsoft.AspNetCore.Authentication.JwtBearer.md` owns why.

## General pitfalls
- **Faking the consumer does not remove the producer's startup requirement:**
  services configured at app-startup config-time (options bound and validated
  during host build, clients constructed eagerly, guards that assert a setting
  is present) run before any test double is resolved. So a test that replaces
  the interface consuming some external system can still fail at host
  construction because the configuration feeding that system is absent. Supply
  dummy configuration values for the startup-time producer even though
  nothing in the test will use them. The error surfaces as a host-build
  failure, not as a missing-dependency message, so it reads as unrelated to
  the substitution. A value read before `Build()` needs one of the early
  configuration paths above, since `ConfigureAppConfiguration` arrives too
  late for it.
- **Background services really run.** Observed in practice: the factory starts
  the whole host, so every registered `IHostedService` and `BackgroundService`
  (queue consumers, schedulers, sweepers) starts with it and needs its
  dependencies. Give them their dependencies, or remove their registrations
  deliberately and test them elsewhere. The integration-testing docs do not
  call this out; it follows from the factory building the app's real host.
- The default `Development` environment turns on whatever the app enables for
  development (developer exception page, user secrets, relaxed settings), so
  a test can pass on behaviour production never has.
- A POST to an MVC or Razor Pages endpoint must pass the antiforgery check.
  The test has to fetch the page, read the antiforgery cookie and token, and
  send both.
- Do not use the EF Core in-memory provider here
  ([Microsoft.EntityFrameworkCore.md](Microsoft.EntityFrameworkCore.md) owns
  why). A real engine in a container is closer
  ([Testcontainers.PostgreSql.md](Testcontainers.PostgreSql.md)).
- With HTTPS redirection middleware the default `http://localhost` base
  address logs redirection warnings; set `BaseAddress = new
  Uri("https://localhost")` in the client options.
- When tests load files relative to `Assembly.Location`, shadow copying runs
  them from another folder; turn it off in `xunit.runner.json`
  (`"shadowCopy": false`).

## Testing
- This package is the test tool. Assert the negative path as well as the
  happy one: an unauthenticated request to a protected endpoint must be
  rejected (`401`, or a redirect for cookie-based UI), because a missing
  authentication setup otherwise passes every positive test
  ([Microsoft.AspNetCore.Authentication.JwtBearer.md](Microsoft.AspNetCore.Authentication.JwtBearer.md)
  owns the opt-in failure mode).
- Keep integration tests to the paths where the components meeting is the
  point. The docs advise a focused set of read, write, update and delete tests
  per store, with unit tests covering the logic.

## Security defaults
- `TestServer` opens no socket; requests never leave the process.
- A test authentication handler accepts every request. Keep it in the test
  project, registered only through the factory, so it can never reach a
  production build. The JWT guidance warns against weakening an API's
  security to make it testable outside a dedicated test environment.

## Operational behaviour
- The host is built lazily, on the first access to `CreateClient()`,
  `Services` or `Server`; that first call pays the full app startup.
- Disposing the factory disposes the clients it created, the factories
  derived through `WithWebHostBuilder`, the `TestServer` and the host. A
  fixture that owns the factory disposes it when its scope ends.
- Configuration changes made through `WithWebHostBuilder` build a second
  host, so each derived factory pays startup again.

## Interop
- xUnit: share the factory through `IClassFixture<>` or a collection fixture
  (`xunit.md`).
- Real infrastructure: start containers in the same fixture and feed their
  connection strings to the app through test configuration
  (`Testcontainers.PostgreSql.md`), and reset data between tests
  (`Respawn.md`).
- Authentication: `Microsoft.AspNetCore.Authentication.JwtBearer.md` for
  the bearer handler's options and test-time relaxation.
- Browser-driven tests of single-page apps are out of scope; the docs point
  to Playwright (`Microsoft.Playwright.md`).

## Major lines

### 6.x line and later (minimal hosting)
- `TEntryPoint` is the implicit `Program` class of a top-level-statements app,
  which is internal unless exposed (see Install). Apps on the older
  `Startup` and `IHostBuilder` pattern use `CreateHostBuilder` or
  `CreateWebHostBuilder` overrides on the factory to change the environment
  or the builder.
- The package version tracks the ASP.NET Core version; one major line of the
  package serves one major line of the runtime.

### 11.x line
- The docs announce, as a preview feature of the 11.x line, a
  `ConfigureWebApplicationBuilder(IHostApplicationBuilder)` override, whose configuration is visible right after
  `WebApplication.CreateBuilder` returns. It closes the gap that
  `ConfigureAppConfiguration` leaves for values read before `Build()`.

## Upstream docs
- Docs: https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests
- Repo: https://github.com/dotnet/aspnetcore
- Package: https://www.nuget.org/packages/Microsoft.AspNetCore.Mvc.Testing
