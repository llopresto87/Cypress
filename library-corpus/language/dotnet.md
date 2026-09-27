# dotnet — language

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
.NET is Microsoft's cross-platform managed application platform: a runtime (CLR),
base class libraries, and an SDK/CLI (`dotnet`) for building C#/F#/VB
applications: web (ASP.NET Core), desktop/mobile (MAUI), console, and services.
Runtime and language versions advance together (a given .NET line ships with a
corresponding C# language version).

## Core API / usage shape
- **Support lifecycle.** A new major ships once a year. Even-numbered majors are
  LTS and odd-numbered majors are STS, with the shorter support window. Patches
  ship monthly and are cumulative, and the support policy requires a system to
  stay current on released patches to count as supported. A release moves from
  active support, to maintenance (security fixes only), to end of life, after
  which no published CVE gets a patch.
- Projects declare a **target framework moniker** (`net<major>.0`) in the
  `.csproj`, typically via `<TargetFramework>`; this can be centralized across a
  solution with `Directory.Build.props`.
- The SDK version can be pinned per-repo with `global.json`, commonly alongside
  a `rollForward` policy that governs which installed SDKs satisfy that pin.
- **Central Package Management (CPM)** via `Directory.Packages.props`
  (`ManagePackageVersionsCentrally=true`, optionally
  `CentralPackageTransitivePinningEnabled=true`) centralizes `PackageVersion`
  entries across all projects in a solution.
- .NET tools (`dotnet tool install`) come as global tools, installed per user,
  or local tools, declared in a repository manifest and restored with the
  repository.

## Idioms & best practices
- Set the target framework and shared build properties centrally
  (`Directory.Build.props`) rather than per-project.
- Use CPM to keep dependency versions consistent across a multi-project solution.
- Prefer a `global.json` with an explicit `rollForward` policy for reproducible
  yet forward-compatible SDK selection.
- Plan a target-framework move as its own piece of work, with its own spec and
  test pass. Changing `net<major>.0` in every project and rebuilding is not a
  pin bump. An approaching end-of-support date is a dated obligation to
  schedule that work, and no test goes red for it.
- Record which runtime patch is deployed, somewhere queryable. Roll-forward
  and floating image tags mean nobody can read it off the repository.
- ASP.NET Core's performance best-practices page, the rules that bite most
  services:
  - Never block on asynchronous work with `Task.Wait()` or `Task<T>.Result`.
    Keep request-path I/O async all the way down.
  - Never write `async void`.
  - Do not create and dispose `HttpClient` instances directly. Register
    outbound clients through `IHttpClientFactory` (`AddHttpClient`), which is
    also where resilience and header-forwarding handlers attach.
  - Use no-tracking queries for read-only data access.
  - Run background work in a hosted service that resolves its own scope through
    `IServiceScopeFactory`, not in a fire-and-forget `Task.Run`.
  - Do not read a large request body into memory whole, and do not assume
    `HttpRequest.ContentLength` is set.
- **Assert a logged audit field at the sink, on the formatted message.** When a
  contract says a field reaches the log store, build a real `LoggerFactory` over
  a capturing provider, call the `[LoggerMessage]` method, and assert on the
  captured entry's formatted message, one case per contracted field. Then remove
  one template placeholder and confirm that exactly that field's case fails.
  An assertion on the structured state cannot see what the sink drops (see the
  console formatter pitfall below).

## General pitfalls
- **`global.json` `rollForward` governs SDK selection at build time only, never
  the runtime.** Running a `net<N>.0` assembly is a separate resolution that
  needs the `net<N>` shared framework installed; if only a newer major runtime
  is present the process fails to *start*, and for `dotnet test` the test host
  aborts before any test is collected, easily misread as an environment or
  daemon problem. The runtime-side fix is the environment variable
  `DOTNET_ROLL_FORWARD=LatestMajor` (or `Major`), not a project-file change. Do
  not read `rollForward` as a promise that the runtime "floats to whatever patch
  is present": the matching framework may be absent. The same variable is what
  lets a global tool built for a newer major run against an older target.
- **Global tools are not on `PATH` in a container build.** `dotnet tool install
  --global` writes to a per-user tools directory that base images do not add to
  `PATH`. Add it explicitly, install to a known `--tool-path`, or use a local
  tool manifest.
- The deployed ASP.NET Core runtime patch and individually-pinned
  `Microsoft.AspNetCore.*` package versions can diverge; each has its own
  version surface to reason about.
- **The default console log formatter writes the formatted message and does not
  enumerate structured state.** A `[LoggerMessage]` parameter with no
  placeholder in the message template never reaches a log store that scrapes
  console output. Find out which formatter is effective before adding a field
  to an audited record.
- **An empty log-level value behaves exactly like an absent key.** For a
  `Logging:LogLevel:*` key, a missing key and an empty string both give the
  framework default floor with no error, while a misspelt level throws when the
  logger is built. So a typo fails loudly and an empty value fails silently. A
  configuration interpolation with no fallback and no required-guard, such as
  `${LOG_LEVEL}` in a compose file, resolves to an empty string when the
  variable is unset, and the service starts at the default level with no warning. To
  enforce a level, fail the deploy on an unset variable or write the value
  literally.
- **Forwarded headers: four traps in `ForwardedHeadersMiddleware`.**
  - The widely copied advice to clear `KnownNetworks` and `KnownProxies` in a
    container comes from the documentation for long-unsupported versions.
    Clearing both lists disables the trust check, so any client that can reach
    the app can forge `X-Forwarded-For`. The remedy upstream gives for an
    unknown proxy is to review the deployment topology.
  - An unknown proxy is skipped silently by design, logged only at debug level,
    and the middleware keeps whatever it processed before the miss. A wrong or
    empty trust set produces no warning, no error and no metric, only a wrong
    `RemoteIpAddress`. Verify the trust set with a deploy-time check, never by
    watching logs.
  - `ForwardLimit` bounds how far the middleware walks the chain; it is not a
    trust control. `ForwardedForHeaderName` is an interop setting for
    appliances with non-standard header names, not a security control.
  - The middleware has long handled only the `X-Forwarded-*` headers, with no
    parser for the standard `Forwarded` header (RFC 7239). Confirm current
    support before designing on `Forwarded`.
- **Message text is not where a byte search looks in a compiled assembly.** In
  the .NET metadata format, string literals live in the `#US` (user strings)
  heap as UTF-16LE, while type and member names live in the `#Strings` heap,
  which is ASCII-compatible. A plain byte search for an ASCII string finds
  identifiers and never message text. Search for the UTF-16LE encoding, or use
  a metadata reader.

## Upstream docs
- https://learn.microsoft.com/en-us/dotnet/: official .NET documentation
- https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core: the
  .NET support policy (LTS/STS, patch currency)
- https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices:
  ASP.NET Core performance best practices
- https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer:
  forwarded headers behind proxies and load balancers
- https://github.com/dotnet/core: .NET source and release-notes repository
