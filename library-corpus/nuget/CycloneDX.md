# CycloneDX — nuget

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The CycloneDX project's software bill of materials (SBOM) generator for .NET. It
reads a solution, a project, or a directory of projects, resolves their NuGet
dependencies, and writes a CycloneDX document listing each component. It ships as
a .NET tool (NuGet package type `DotnetTool`), not as a library a project
references.

Its names differ by surface, and a search needs all of them:

| Where | Name |
|---|---|
| NuGet package ID (what `dotnet tool install` takes) | `CycloneDX` |
| Command it installs | `dotnet-CycloneDX` |
| Also invocable as | `dotnet CycloneDX`, through the .NET CLI's `dotnet-<verb>` convention |
| Upstream repository | `CycloneDX/cyclonedx-dotnet` |

## Core API / usage shape
- Install: `dotnet tool install --global CycloneDX`, or as a local tool through a
  tool manifest.
- Invoke with a path and an output directory:
  `dotnet-CycloneDX <solution.sln | project.csproj | directory> -o <dir>`.
- Main switches: `-o`/`--output` (output directory), `-fn`/`--filename` (file
  name), `-F`/`--output-format` (XML or JSON), `-rs`/`--recursive` (follow
  project references from a single project file), `-ef`/`--exclude-filter`
  (comma-separated `name@version`, or a bare `name` for every version, to leave
  out along with their transitive dependencies). `-F` also takes `Auto`, the
  default, and `UnsafeJson` (relaxed escaping).

## Idioms & best practices
- Bake the tool into the scanning image at an exact version. Installing it
  lazily at scan time adds a mandatory network call mid-scan and can bring a
  different version on every run.
- Pin the generator exactly wherever it produces evidence. An SBOM from a
  different generator version is not directly comparable to the one before it.
- Prefer a repository tool manifest (`dotnet tool restore`) for developer and CI
  machines, which pins the version in source control and needs no global `PATH`
  entry.

## General pitfalls
- `dotnet CycloneDX` (two words) is not a subcommand the tool registers. It
  works only because the .NET CLI runs any `dotnet-<verb>` executable it finds
  on `PATH`. Searching the codebase for `dotnet-CycloneDX` and `dotnet CycloneDX`
  as unrelated strings misses half the invocations.
- A global install lands in a per-user tools directory that container builds do
  not put on `PATH`, so the image builds and the first SBOM run fails with
  "command not found". The general .NET global-tool fact lives in
  `../language/dotnet.md`.
- A generator version bump changes the artifacts. Regenerate and diff before
  moving the pin.
- A wrapper that treats a missing tool as a warning and exits 0 yields a green
  step with an SBOM missing. Fail the step, and assert each expected SBOM exists.

## Upstream docs
- Repo and usage: https://github.com/CycloneDX/cyclonedx-dotnet
- Package: https://www.nuget.org/packages/CycloneDX
- .NET tools (install locations, `dotnet-<verb>` convention): https://learn.microsoft.com/en-us/dotnet/core/tools/global-tools
- Specification: https://cyclonedx.org/specification/overview/
