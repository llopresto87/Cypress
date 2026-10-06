# dotnet — language

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
.NET is Microsoft's cross-platform managed application platform: a runtime (CLR),
base class libraries, and an SDK/CLI (`dotnet`) for building C#/F#/VB
applications: web (ASP.NET Core), desktop/mobile (MAUI), console, and services.
Runtime and language versions advance together (a given .NET line ships with a
corresponding C# language version). The runtime, the libraries and the SDK are
open source under the MIT licence, developed in the `dotnet/runtime`,
`dotnet/aspnetcore` and `dotnet/sdk` repositories, with release notes in
`dotnet/core`.

## Install, setup and configuration
- Install the SDK to build and the runtime (or the ASP.NET Core runtime) to
  run. Major and minor lines install side by side; a servicing update replaces
  the previous patch of the same line. Upstream recommends the platform
  installers or packages for a development machine, and the `dotnet-install`
  scripts for CI, where the install is unattended, needs no admin rights and
  does not have to survive the run.
- **SDK selection.** The `dotnet` muxer looks for a `global.json` from the
  current working directory upward; the MSBuild SDK resolver starts from the
  solution or project directory. With no `global.json`, the highest installed
  SDK wins. `sdk.version` must be a full version (no wildcards or ranges), and
  with a version but no `rollForward` the policy is `patch`. The other values
  are `feature`, `minor`, `major`, `latestPatch`, `latestFeature`,
  `latestMinor`, `latestMajor` and `disable` (exact match). The SDK's third
  version field is the *feature band* (hundreds), which can bring a new
  MSBuild or NuGet, so a feature-band move is a toolchain change.
- **Runtime selection** is separate. An app built for a major and minor line
  uses the latest installed patch of that line automatically; by default it
  rolls forward to a newer minor of the same major when its own is missing,
  never to a newer major. The policy comes from the app's
  `*.runtimeconfig.json`, then the `DOTNET_ROLL_FORWARD` environment variable,
  then a `--roll-forward` argument, each overriding the one before.
- **Project-wide settings.** Projects declare a **target framework moniker**
  (`net<major>.0`) in `<TargetFramework>`; centralize it and shared properties
  in `Directory.Build.props`. The default C# version follows the target
  framework.
- **Central Package Management (CPM).** A `Directory.Packages.props` with
  `ManagePackageVersionsCentrally=true` holds one `<PackageVersion>` per
  package; projects then reference packages without a version.
  `VersionOverride` on a single `<PackageReference>` wins over the central
  version. `CentralPackageTransitivePinningEnabled=true` also pins transitive
  dependencies, and a pin lower than a dependency asks for fails restore.
- **.NET tools** come as global tools (per user, in `~/.dotnet/tools`), as
  tool-path tools (installed into a directory you name), or as local tools,
  declared in a `.config/dotnet-tools.json` manifest and restored with the
  repository.
- **CLI environment.** The SDK collects usage telemetry unless
  `DOTNET_CLI_TELEMETRY_OPTOUT` is set to `true`; `DOTNET_NOLOGO` silences the
  first-run banner.
- **Support lifecycle.** A new major ships once a year, in November.
  Even-numbered majors are LTS, supported for three years, and odd-numbered
  majors are STS, supported for two. Because a new major ships every year, an
  STS line and the LTS line before it can reach end of support together. Patches
  ship monthly and are cumulative, and the support policy requires a system to
  stay current on released patches to count as supported. A release moves from
  active support, to maintenance (security fixes only, the final six months), to
  end of life, after which no published CVE gets a patch. Setting the MSBuild
  property `CheckSdkVulnerabilities` to `true` makes the build warn when the
  resolved SDK is out of support.

## Core API / usage shape
- The CLI verbs: `dotnet new`, `restore`, `build`, `test`, `run`, `publish`,
  `pack`, plus `dotnet tool` and the package commands.
- SDK pinning: see `global.json` under Install, setup and configuration.
- **Generic Host.** `Host.CreateApplicationBuilder` (and
  `WebApplication.CreateBuilder` for ASP.NET Core) wires configuration, logging,
  dependency injection and hosted services into one object that owns startup
  and graceful shutdown. Inject `IHostApplicationLifetime` to hook started,
  stopping and stopped.
- **Log redaction.** `Microsoft.Extensions.Compliance.Redaction`
  (`services.AddRedaction(...)`) maps data classifications to redactors, and
  `builder.Logging.EnableRedaction()` (from `Microsoft.Extensions.Telemetry`)
  applies them when a classified `[LoggerMessage]` parameter is logged, not at
  each call site. The default redactor erases the value; the HMAC redactor
  needs a secret key and still raises an experimental-API warning.

## Idioms & best practices
- Set the target framework and shared build properties centrally
  (`Directory.Build.props`) rather than per-project.
- Use CPM to keep dependency versions consistent across a multi-project solution.
- Prefer a `global.json` with an explicit `rollForward` policy for reproducible
  yet forward-compatible SDK selection. Upstream advises `disable` when the
  repository uses package lock files, so the SDK and the dependency graph move
  together.
- Do not set `LangVersion` to `latest`: upstream warns that it varies from
  machine to machine and can enable features the target runtime lacks. Let the
  target framework choose the language version.
- Plan a target-framework move as its own piece of work, with its own spec and
  test pass. Changing `net<major>.0` in every project and rebuilding is not a
  pin bump. An approaching end-of-support date is a dated obligation to
  schedule that work, and no test goes red for it.
- Record which runtime patch is deployed, somewhere queryable. Roll-forward
  and floating image tags mean nobody can read it off the repository.
- ASP.NET Core's performance best-practices page, the rules that bite most
  services:
  - Never block on asynchronous work with `Task.Wait()` or `Task<T>.Result`.
    Keep request-path I/O async all the way down. Synchronous body reads block
    a thread the same way: `HttpContext.Request.Form` is sync over async, so
    call `ReadFormAsync`, and read the body stream asynchronously.
  - Never write `async void`.
  - Do not create and dispose `HttpClient` instances directly. Register
    outbound clients through `IHttpClientFactory` (`AddHttpClient`), which pools
    and recycles the message handlers (default handler lifetime two minutes, so
    DNS changes are picked up) and is also where resilience and
    header-forwarding handlers attach.
  - Use no-tracking queries for read-only data access.
  - Run background work in a hosted service that resolves its own scope through
    `IServiceScopeFactory`, not in a fire-and-forget `Task.Run`.
  - `HttpContext` is valid only while its request is in the pipeline. Do not
    store it in a field, use it from several threads, or capture it, or a
    scoped service such as a `DbContext`, in work that outlives the request;
    copy the data the work needs instead. Upstream's example of late access
    crashes the process.
  - Do not read a large request body into memory whole, and do not assume
    `HttpRequest.ContentLength` is set.
- **Assert a logged audit field at the sink, on the formatted message.** When a
  contract says a field reaches the log store, build a real `LoggerFactory` over
  a capturing provider, call the `[LoggerMessage]` method, and assert on the
  captured entry's formatted message, one case per contracted field. Then remove
  one template placeholder and confirm that exactly that field's case fails.
  An assertion on the structured state cannot see what the sink drops (see the
  console formatter pitfall below). This test shape is observed in practice;
  the logging docs do not prescribe it.

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
- **Global tools are not on `PATH` in a container build.** Observed in
  practice: `dotnet tool install --global` writes to `~/.dotnet/tools`, and in
  an image build that directory is not on `PATH`. Upstream says the SDK adds it
  to the user's path on first run (`DOTNET_ADD_GLOBAL_TOOLS_TO_PATH`, default
  on), which does not reach a later non-interactive build step. Add the
  directory explicitly, install to a known `--tool-path`, or use a local tool
  manifest. The official SDK images take the `--tool-path` route for the
  PowerShell they ship.
- The deployed ASP.NET Core runtime patch and individually-pinned
  `Microsoft.AspNetCore.*` package versions can diverge; each has its own
  version surface to reason about.
- **Large objects cost a full collection.** An allocation of 85,000 bytes or
  more lands on the large object heap, which only a generation 2 collection
  cleans. Buffering an upload into a `byte[]` or materializing a large
  collection per request causes pauses, and on a large enough body upstream
  warns of out-of-memory and denial of service. Stream instead, and pool large
  buffers with `ArrayPool<T>`.
- **The default console log formatter writes the formatted message and does not
  enumerate structured state.** Observed in practice: a `[LoggerMessage]`
  parameter with no placeholder in the message template never reaches a log
  store that scrapes console output. The docs name `Simple` as the default
  formatter and do not say what it drops; `AddJsonConsole` is the documented
  alternative. Find out which formatter is effective before adding a field to
  an audited record.
- **An empty log-level value behaves exactly like an absent key.** Observed in
  practice: for a `Logging:LogLevel:*` key, a missing key and an empty string
  both give the framework default floor with no error, while a misspelt level
  throws when the logger is built. So a typo fails loudly and an empty value
  fails silently. The docs state only that the default level is `Information`
  when none is set. A configuration interpolation with no fallback and no
  required-guard, such as `${LOG_LEVEL}` in a compose file, resolves to an empty
  string when the variable is unset, and the service starts at the default
  level with no warning. To enforce a level, fail the deploy on an unset
  variable or write the value literally.
- **Forwarded headers: the traps in `ForwardedHeadersMiddleware`.**
  - By default only loopback addresses are trusted as proxies, only one proxy
    hop is processed (`ForwardLimit` 1, read right to left), and no header is
    forwarded until `ForwardedHeaders` names it. `KnownProxies` matches exact
    addresses and `KnownNetworks` matches CIDR ranges; on a dual-mode socket an
    IPv4 peer appears in IPv6-mapped form (`::ffff:<ipv4>`), so a plain IPv4
    entry may never match. Behind a container network, add the proxy's address
    or subnet explicitly.
  - The widely copied advice to clear `KnownNetworks` and `KnownProxies` in a
    container comes from the documentation for long-unsupported versions.
    Clearing both lists disables the trust check, so any client that can reach
    the app can forge `X-Forwarded-For`. The remedy upstream gives for an
    unknown proxy is to review the deployment topology. The
    `ASPNETCORE_FORWARDEDHEADERS_ENABLED=true` shortcut likewise applies no
    known-proxy restriction, by upstream's own warning.
  - An unknown proxy is skipped silently by design, logged only at debug level,
    and the middleware keeps whatever it processed before the miss. A wrong or
    empty trust set produces no warning, no error and no metric, only a wrong
    `RemoteIpAddress`. Verify the trust set with a deploy-time check, never by
    watching logs.
  - Releases without a later upstream fix skipped the known-proxy check
    entirely when `X-Forwarded-For` was not among the forwarded headers, so
    forwarding only `X-Forwarded-Proto` or `X-Forwarded-Host` trusted any
    peer. Stay on current patches, and forward `X-Forwarded-For` alongside.
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

## Testing
- `dotnet test` builds and runs tests through a test platform: VSTest, the
  long-standing default, or Microsoft.Testing.Platform (MTP), selectable from
  the 10 SDK line in `global.json` (`"test": { "runner":
  "Microsoft.Testing.Platform" }`). The runner decides which command-line
  options exist, so a CI script written for one may not parse under the other.
- The common frameworks are MSTest, NUnit and xUnit.net, which support both
  platforms, and TUnit, which runs only on MTP.
- ASP.NET Core integration tests host the app in memory; see
  [`Microsoft.AspNetCore.Mvc.Testing`](../nuget/Microsoft.AspNetCore.Mvc.Testing.md).
- A test host that cannot find its target runtime aborts before collecting
  any test; see the roll-forward pitfall above.

## Security defaults
- **Patch currency is the security posture.** Patch roll-forward is automatic
  within a line so that security fixes apply as soon as they are installed; a
  line out of support gets no fixes at all.
- **Containers.** From the 8 line the official Linux images define a non-root
  `app` user (opt in with `USER app`), and ASP.NET Core images listen on port
  8080, not 80. `ASPNETCORE_HTTP_PORTS` sets the ports.
- **HTTPS.** `UseHttpsRedirection` and `UseHsts` are middleware the app adds. Behind a
  TLS-terminating proxy that already redirects and sends HSTS, the app needs
  neither, but it then depends on forwarded headers to know the original
  scheme.
- **Tools run with full trust.** A global tool is a NuGet package that runs as
  the user and lands on `PATH`; install tools only from authors you trust.
- **Dependency audit.** Restore audits packages against known advisories; from
  the 10 line, projects targeting it audit transitive packages too
  (`NuGetAuditMode` defaults to `all`), which can fail a build that treats
  warnings as errors.
- **Redact in the pipeline.** Use the redaction library above, not
  hand-masking at call sites, and keep the HMAC redactor's key secret and
  distinct per deployment.

## Operational behaviour
- **Startup and runtime resolution.** A framework-dependent app starts only if
  a matching shared framework is installed (see the roll-forward pitfall). A
  self-contained app carries its own runtime and is patched only by
  republishing.
- **Shutdown.** The host stops hosted services and then the server within a
  shutdown timeout (default 30 seconds). Kestrel closes its port bindings and
  tells open connections to stop taking new requests. From the 10 line the runtime leaves
  termination signals to the operating system: the Generic Host and ASP.NET
  Core handle SIGTERM, but in a bare console app SIGTERM ends the process at
  once and `ProcessExit` does not run.
- **Garbage collection.** Workstation GC is the default for standalone apps,
  the host chooses for hosted apps, and background GC is on by default. Server
  GC gives each logical CPU its own heap and GC thread and treats the process
  as the machine's main tenant, so many server-GC processes on one host
  contend. From the 9 line, DATAS (dynamic adaptation to application sizes) is
  on by default: it starts with one heap and grows or shrinks the heap count
  and budget with the live data size, trading a little peak throughput for a
  much smaller working set. Turn it off with
  `DOTNET_GCDynamicAdaptationMode=0` if throughput drops.
- **Container sizing.** The size-optimized images (Alpine, distroless,
  chiseled) omit ICU and tzdata and need
  `<InvariantGlobalization>true</InvariantGlobalization>`.

## Interop
- **Containers.** The official SDK images set `DOTNET_SDK_VERSION` in their
  environment and ship PowerShell (`pwsh`) installed as a .NET tool, so a build
  step can read the SDK version without running `dotnet`.
- **Reverse proxies and load balancers:** through `ForwardedHeadersMiddleware`
  (see the pitfalls). Behind IIS, `UseIISIntegration` configures it; nothing
  configures it automatically behind a Linux proxy.
- **NuGet:** the package manager is built into the SDK (`dotnet restore`,
  `dotnet add package`); package pages in this corpus live under `nuget/`.
- **Log stores** that scrape console output see only what the console
  formatter writes (see the pitfalls).

## Major lines

### 8.x line
- LTS. Ships C# 12 (primary constructors on classes, collection expressions).
- Container images gain the non-root `app` user and move the default
  ASP.NET Core port from 80 to 8080. The image stops setting
  `ASPNETCORE_URLS`, so an app built on the older
  `WebHost.CreateDefaultBuilder` falls back to `http://localhost:5000`.
- DATAS exists as an opt-in.

### 9.x line
- STS. Ships C# 13.
- DATAS is on by default.

### 10.x line
- LTS. Ships C# 14.
- `dotnet test` can run on Microsoft.Testing.Platform; `dotnet tool exec` and
  the `dnx` script run a tool once without installing it; the CLI accepts
  noun-first commands such as `dotnet package add`.
- Default container tags are Ubuntu-based, and upstream stops publishing
  Debian images.
- The runtime installs no termination-signal handlers of its own (see
  Operational behaviour).
- NuGet audit covers transitive packages by default for projects targeting
  the line.

## Upstream docs
- https://learn.microsoft.com/en-us/dotnet/: official .NET documentation
- https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core: the
  .NET support policy (LTS/STS, patch currency)
- https://learn.microsoft.com/en-us/dotnet/core/releases-and-support: release
  types, feature bands, roll-forward
- https://learn.microsoft.com/en-us/dotnet/core/tools/global-json: SDK
  selection and `rollForward`
- https://learn.microsoft.com/en-us/dotnet/core/versions/selection: runtime
  selection and `DOTNET_ROLL_FORWARD`
- https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management:
  Central Package Management
- https://learn.microsoft.com/en-us/dotnet/core/runtime-config/garbage-collector:
  GC settings, including DATAS
- https://learn.microsoft.com/en-us/dotnet/core/extensions/data-redaction:
  log redaction
- https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices:
  ASP.NET Core performance best practices
- https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer:
  forwarded headers behind proxies and load balancers
- https://learn.microsoft.com/en-us/dotnet/core/compatibility/breaking-changes:
  breaking changes per major line
- https://github.com/dotnet/core: .NET source and release-notes repository
