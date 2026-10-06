# CycloneDX — nuget

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions — for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The CycloneDX project's software bill of materials (SBOM) generator for .NET. It
reads a project, a solution, or a directory of projects, resolves their NuGet
dependencies, and writes a CycloneDX document listing each component. It ships as
a .NET tool (NuGet package type `DotnetTool`), not as a library a project
references, and also as the `cyclonedx/cyclonedx-dotnet` container image.
Licence: Apache-2.0.

Its names differ by surface, and a search needs all of them:

| Where | Name |
|---|---|
| NuGet package ID (what `dotnet tool install` takes) | `CycloneDX` |
| Command it installs | `dotnet-CycloneDX` |
| Also invocable as | `dotnet CycloneDX`, through the .NET CLI's `dotnet-<verb>` convention |
| Upstream repository | `CycloneDX/cyclonedx-dotnet` |
| Container image | `cyclonedx/cyclonedx-dotnet` |

## Install, setup and configuration
- Global: `dotnet tool install --global CycloneDX`, with `--version <x>` to pin
  and `dotnet tool update --global CycloneDX` to move. Location and `PATH`
  rules for .NET tools, and their full-trust model, live in
  [`../language/dotnet.md`](../language/dotnet.md).
- Local: `dotnet new tool-manifest`, then `dotnet tool install CycloneDX`
  without `--global`. The version is recorded in `.config/dotnet-tools.json`,
  `dotnet tool restore` installs it on another machine, and
  `dotnet tool run <command>` runs it. Keep the manifest under review: the CLI
  runs whatever it lists, in full trust.
- Container: `docker run --rm --user $(id -u):$(id -g) -v $(pwd):/work cyclonedx/cyclonedx-dotnet [options] /work/<path>`.
  The `--user` flag lets `dotnet restore` write `obj/` into the mounted tree and
  leaves the output owned by you.
- Inputs: a `.csproj` (or `.fsproj`, `.vbproj`), a `.sln`, `.slnf` or `.slnx`,
  a `packages.config`, or a directory that is scanned for `packages.config`
  files.
- By default the tool runs `dotnet restore` itself and reads the resulting
  `obj/project.assets.json`. `-dpr` / `--disable-package-restore` skips that
  and reads what an earlier restore wrote.
- Private feeds: `-u` / `--url` with credentials. Pass the credentials through
  `CYCLONEDX_NUGET_USERNAME` and `CYCLONEDX_NUGET_PASSWORD`, not the `-us` /
  `-usp` flags, so they stay out of process listings and CI logs. A flag wins
  over its variable when both are set.

## Core API / usage shape
- Invoke with a path and an output directory:
  `dotnet-CycloneDX <project.csproj | solution.sln | directory> -o <dir>`.
  Without `-o`, the output goes to the working directory.
- Output: `-fn` / `--filename` (default `bom.xml` or `bom.json`), `-F` /
  `--output-format` (`Auto`, the default, `Json`, `Xml`, or `UnsafeJson` with
  relaxed escaping), `-spv` / `--spec-version` (the CycloneDX schema version
  to write).
- Scope: `-tfm` / `--framework` and `-rt` / `--runtime` select one target
  (otherwise all are aggregated); `-ed` / `--exclude-dev` drops development
  dependencies; `-t` / `--exclude-test-projects`; `-ef` / `--exclude-filter`
  (comma-separated `name@version`, or a bare `name` for every version, removed
  together with their transitive dependencies); `-ipr` /
  `--include-project-references` lists project references as components;
  `-rs` / `--recursive` follows project references from a single project file.
- BOM metadata: `-sn` / `--set-name`, `-sv` / `--set-version` (default `0.0.0`
  unless the project file has `<Version>`, `<AssemblyVersion>`,
  `<ProjectVersion>` or `<PackageVersion>`), `-st` / `--set-type` (default
  `Application`), `--set-nuget-purl`, and `-imp` / `--import-metadata-path` for
  a template BOM whose `<metadata>` block is reused. Precedence: flags, then the
  template, then the project file, then defaults.
- Reproducibility and speed: `-ns` / `--no-serial-number` omits the random
  serial number; `-dhc` / `--disable-hash-computation` skips package hashes;
  `-dct` sets the `dotnet` command timeout (default 300000 ms).
- Licences: GitHub licence resolution is off unless `-egl` /
  `--enable-github-licenses` is set. With it on, add a token (`-gt` with
  `-gu`, or `-gbt`, or the `CYCLONEDX_GITHUB_*` / `GITHUB_TOKEN` variables).

## Idioms & best practices
- Point the tool at the root `.csproj` of the artifact you ship. Its restore
  output already holds the full closure, including project references, so
  `--recursive` is not needed for SDK-style projects. Upstream advises against
  a `.sln` input: a solution has no single dependency closure, so its SBOM is
  the union of every project in it.
- Restore first with the configuration you ship
  (`dotnet restore app.csproj -p:Configuration=Release`), then run the tool
  with `--disable-package-restore`. Packages conditional on the configuration
  then match the artifact, and the SBOM step needs no feed access.
- For a multi-targeted project, pass `--framework` and `--runtime` so the
  SBOM matches the shipped build.
- Keep a metadata template with the organisation's defaults and set only the
  version per build with `--set-version`.
- Bake the tool into the scanning image at an exact version. Installing it
  lazily at scan time adds a mandatory network call mid-scan and can bring a
  different version on every run.
- Observed in practice: in an image build, run `dotnet CycloneDX --version` in
  the same `RUN` step that installs the tool. A missing `PATH` entry then fails
  the build instead of the first scan. Upstream only notes that the tools
  directory must be on `PATH`.
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
- A generator version bump changes the artifacts: a new major line can write a
  newer CycloneDX schema version and move fields. Regenerate and diff before
  moving the pin.
- Observed in practice: a wrapper that treats a missing tool as a warning and
  exits 0 yields a green step with an SBOM missing. Fail the step, and assert each expected SBOM exists.
- A package resolved by NuGet but absent from the binary output (a
  .NET Standard facade pulled in by an old dependency, say) still appears in the
  SBOM. Remove it with `--exclude-filter`.
- With GitHub licence resolution on and no token, the unauthenticated limit is
  60 calls per hour. Past it, generation fails on purpose, so the licence list
  is never silently incomplete.
- A restore without the shipping configuration lists the wrong packages when
  `PackageReference` items carry a `Condition`.

## Testing
- Upstream documents no testing pattern for consumers of the tool. Observed in
  practice: fail the step when the tool is missing, and assert each expected
  SBOM exists (see General pitfalls).
- Upstream's own suite runs end-to-end tests with Testcontainers and Verify
  snapshots. That suite is internal to upstream, not a consumer pattern.

## Security defaults
- The tool runs `dotnet restore`, which evaluates the project's MSBuild files
  and contacts the configured feeds. Scan only trees you would build.
- Install the tool only from the official package and keep a local tool
  manifest under review. The trust model of .NET tools is in
  [`../language/dotnet.md`](../language/dotnet.md).
- Credentials for feeds and GitHub belong in the `CYCLONEDX_*` environment
  variables. A flag value is visible in process listings, shell history and CI
  logs.
- Container image: upstream's README and its rootless-container decision record
  say the image runs as root by default, while the release notes of a later
  6.x release say it now runs as a non-root user. Pass
  `--user $(id -u):$(id -g)` either way.

## Operational behaviour
- One run is one process: restore (unless disabled), read
  `project.assets.json`, resolve licences and hashes, write the file, exit.
- `-dct` exists mainly for long restores; raise it for slow feeds. Hash
  computation and GitHub licence lookups add their own time and can be turned
  off or left off.
- If the `obj` folder is relocated, pass `-biop` /
  `--base-intermediate-output-path` so the tool finds the restore output.
- Each run gets a new serial number and timestamp unless you pass
  `--no-serial-number`, so two runs over the same tree are not byte-identical.

## Interop
- NuGet and MSBuild: the dependency graph comes from NuGet's
  `project.assets.json`, so anything that changes restore (configuration,
  target framework, runtime identifier) changes the SBOM.
- CycloneDX consumers: when a consumer accepts only an older schema, write
  that version with `--spec-version`.
- The tool covers NuGet dependencies only. Other ecosystems in the same
  product need their own CycloneDX generators.

## Major lines
The tool's major line decides which .NET runtimes can run it and which
CycloneDX schema it writes by default. It can still scan applications that
target older .NET.

### 3.x line
- Moves the CLI to `System.CommandLine` and writes CycloneDX 1.5. GitHub
  licence resolution becomes opt-in (`-egl`). `-d`, `-r`, `-f` and `--out`
  are deprecated in favour of `-ed`, `-rs`, `-fn` and `--output`; `--output`
  becomes optional. Adds `-ipr`.

### 4.x line
- Writes CycloneDX 1.6. A component's author moves to the `authors` field.

### 5.x line
- The tool itself stops running on .NET 6 and 7; packages carry .NET 8 and
  .NET 9 builds. During the line, `.slnx` input, `--output-format` (which
  deprecates `--json`) and `--spec-version` arrive.

### 6.x line
- Packages carry .NET 8, 9 and 10 builds. The deprecated `-f`, `-d`, `-r` and
  `--disable-github-licenses` flags are removed; `--out` and `--json` remain
  but are still deprecated. The move to stable `System.CommandLine` can change
  parsing in edge cases.
- The first 6.x release notes say the tool now requires the .NET 10 runtime.
  The published package still ships `net8.0`, `net9.0` and `net10.0` tool
  builds. Check the package for the version you pin.
- Later 6.x releases write CycloneDX 1.7 by default and add a
  `--configuration` / `-c` option that passes the configuration to restore.

## Upstream docs
- Repo and usage: https://github.com/CycloneDX/cyclonedx-dotnet
- Best practices: https://github.com/CycloneDX/cyclonedx-dotnet/blob/master/docs/best-practices.md
- BOM metadata: https://github.com/CycloneDX/cyclonedx-dotnet/blob/master/docs/bom-metadata.md
- Releases: https://github.com/CycloneDX/cyclonedx-dotnet/releases
- Package: https://www.nuget.org/packages/CycloneDX
- .NET tools (install locations, `dotnet-<verb>` convention): https://learn.microsoft.com/en-us/dotnet/core/tools/global-tools
- Specification: https://cyclonedx.org/specification/overview/
