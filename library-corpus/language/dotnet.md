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
- With `rollForward: major` (or similar), the effective SDK/runtime patch at
  build/run time is not fixed by the pin — it floats to whatever compatible
  patch is present in the environment, so the running runtime is determined by
  the host/image, not by repo files alone.
- The deployed ASP.NET Core runtime patch and individually-pinned
  `Microsoft.AspNetCore.*` package versions can diverge; each has its own
  version surface to reason about.

## Upstream docs
- https://learn.microsoft.com/en-us/dotnet/ — official .NET documentation
- https://github.com/dotnet/core — .NET source and release-notes repository
