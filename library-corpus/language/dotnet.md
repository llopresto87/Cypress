# dotnet — language

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
.NET is Microsoft's cross-platform managed application platform: a runtime (CLR),
base class libraries, and an SDK/CLI (`dotnet`) for building C#/F#/VB
applications — web (ASP.NET Core), desktop/mobile (MAUI), console, and services.
Runtime and language versions advance together (a given .NET line ships with a
corresponding C# language version).

## Core API / usage shape
- Projects declare a **target framework moniker** (`net<major>.0`) in the
  `.csproj`, typically via `<TargetFramework>`; this can be centralized across a
  solution with `Directory.Build.props`.
- The SDK version can be pinned per-repo with `global.json`, commonly alongside
  a `rollForward` policy that governs which installed SDKs satisfy that pin.
- **Central Package Management (CPM)** via `Directory.Packages.props`
  (`ManagePackageVersionsCentrally=true`, optionally
  `CentralPackageTransitivePinningEnabled=true`) centralizes `PackageVersion`
  entries across all projects in a solution.

## Idioms & best practices
- Set the target framework and shared build properties centrally
  (`Directory.Build.props`) rather than per-project.
- Use CPM to keep dependency versions consistent across a multi-project solution.
- Prefer a `global.json` with an explicit `rollForward` policy for reproducible
  yet forward-compatible SDK selection.

## General pitfalls
- **`global.json` `rollForward` governs SDK selection at build time only, never
  the runtime.** Running a `net<N>.0` assembly is a separate resolution that
  needs the `net<N>` shared framework installed; if only a newer major runtime
  is present the process fails to *start*, and for `dotnet test` the test host
  aborts before any test is collected — easily misread as an environment or
  daemon problem. The runtime-side fix is the environment variable
  `DOTNET_ROLL_FORWARD=LatestMajor` (or `Major`), not a project-file change. Do
  not read `rollForward` as a promise that the runtime "floats to whatever patch
  is present": the matching framework may be absent.
- The deployed ASP.NET Core runtime patch and individually-pinned
  `Microsoft.AspNetCore.*` package versions can diverge; each has its own
  version surface to reason about.

## Upstream docs
- https://learn.microsoft.com/en-us/dotnet/ — official .NET documentation
- https://github.com/dotnet/core — .NET source and release-notes repository
