# Microsoft.AspNetCore.Mvc.Testing — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The official integration-testing host for ASP.NET Core. It provides
`WebApplicationFactory<TEntryPoint>`, which boots the **real application
in-process** — real routing, real middleware, real model binding, real DI — and
lets tests substitute individual services at the seams. The point is a real
pipeline with a few chosen boundaries faked, not a mocked imitation of one.

## Core API / usage shape
- Subclass `WebApplicationFactory<TEntryPoint>` and override `ConfigureWebHost`
  (or use `WithWebHostBuilder`) to reach the host builder from a test fixture.
- Inside it, `ConfigureTestServices` is the substitution point: it runs **after**
  the app's own registrations, so replacing a service there wins over what
  `Program`/`Startup` registered.
- Swap **one specific boundary** per concern — an outbound HTTP client, a clock,
  a message broker — or replace the authentication handler with a test-only,
  header-driven scheme so tests can assert authorization without a real identity
  provider.
- `factory.CreateClient()` returns an `HttpClient` wired to the in-process
  server; requests go through the full pipeline without a network listener or a
  port.

## Idioms & best practices
- Own the factory in a shared test fixture and create a fresh client per test —
  it is expensive to build and safe to share (`xunit.md` owns the
  collection-fixture mechanism).
- Prefer substituting at an owned abstraction (the app's own interface for an
  external system) over intercepting transport, so the test names the boundary
  it is faking.
- Keep the real pipeline intact: every piece of middleware removed to make a test
  pass is a piece of production behavior the test stops covering.

## General pitfalls
- **Faking the consumer does not remove the producer's startup requirement:**
  services configured at app-startup config-time — options bound and validated
  during host build, clients constructed eagerly, guards that assert a setting is
  present — run before any test double is resolved. So a test that replaces the
  interface consuming some external system can still fail at host construction
  because the configuration feeding that system is absent. The fix is to supply
  dummy configuration values for the startup-time producer even though nothing in
  the test will ever use them; the error surfaces as a host-build failure, not as
  a missing-dependency message, so it reads as unrelated to the substitution.

## Upstream docs
- https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests
- https://github.com/dotnet/aspnetcore
- https://www.nuget.org/packages/Microsoft.AspNetCore.Mvc.Testing
