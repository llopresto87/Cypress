# trivy — cli

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a tool, not a record of one
> project's versions. Trivy usually arrives as a container image, a release
> archive or a host package, not from a project lockfile, so the version that
> matters is the one the pipeline runs: record it with `ingest-library` in the
> project's own page, and re-check every flag marked experimental below against
> that version.

## What it is
Trivy is an open-source security scanner (Apache-2.0) maintained by Aqua
Security in the `aquasecurity/trivy` repository, with its documentation at
trivy.dev. One binary scans a **target** with one or more **scanners**:

- targets: `image`, `fs`, `rootfs`, `repo`, `config`, `sbom`, `vm`, `k8s`;
- scanners (`--scanners`): `vuln`, `secret`, `misconfig`, `license`, `crypto`.

It builds an inventory of the target (OS packages, language lockfiles, files,
an SBOM) and matches it against databases it downloads. It never runs the
target. Other subcommands are `server`, `clean`, `plugin`, `module`,
`registry`, `vex`, `convert` and `version`. Upstream does not support Trivy as a
Go library; the CLI is the interface.

## Install, setup and configuration
- **Channels.** Official: the container image (`aquasec/trivy` on Docker Hub,
  also on GHCR and ECR Public), the GitHub release archive, the install script,
  the RPM and DEB repositories, Homebrew and a Windows zip. Other distro
  packages are community-maintained.
- **Precedence.** A flag beats an environment variable, which beats the config
  file. An environment name is `TRIVY_` plus the flag name in upper case with
  `-` as `_` (`TRIVY_CACHE_DIR`, `TRIVY_SEVERITY`).
- **Config file.** `trivy.yaml` is read from the current directory by default;
  `--config`/`-c` picks another path and an empty value disables loading. Keys
  nest by flag group (`scan.skip-dirs`, `scan.scanners`, `vulnerability.*`,
  `db.*`, `cache.*`), while report keys (`format`, `exit-code`, `severity`) sit
  at the top level. Upstream publishes a JSON schema for the file.
- **Defaults worth knowing.** `--severity` covers UNKNOWN through CRITICAL;
  `--format table`; `--exit-code 0`; `--timeout 5m0s`; `--parallel 5`;
  `--pkg-types os,library`; `--image-src docker,containerd,podman,remote`;
  `--ignorefile .trivyignore`. For `image` and `fs` the scanners default to
  `vuln,secret`. (The getting-started page calls vuln "the default scanner";
  the flag reference and the container-image page both say vuln plus secret.)
- **Databases.** Three are fetched on demand: the vulnerability DB (vuln
  scanning only), the Java index DB (identifying JARs only) and the checks
  bundle (misconfiguration only). They come from `mirror.gcr.io` first, then
  `ghcr.io`. `--db-repository`, `--java-db-repository` and
  `--checks-bundle-repository` take OCI addresses; several values fall back in
  order on transient errors such as 429 or 5xx.
- **Cache.** One directory holds the scan cache, both DBs, the checks and VEX
  repositories; `--cache-dir` or `TRIVY_CACHE_DIR` moves it. The DB is
  `db/trivy.db` plus `db/metadata.json`; the Java DB is under `java-db/`.
  `trivy clean --scan-cache|--vuln-db|--java-db|--checks-bundle|--all` removes
  parts. Observed in practice: with no `--cache-dir`, a Linux host uses
  `~/.cache/trivy` (the flag reference shows only a placeholder).
- **Telemetry.** `--disable-telemetry` stops anonymous usage data;
  `--skip-version-check` silences the non-blocking update notice.

## Core API / usage shape
```
trivy image <ref>                      # sources tried in --image-src order
trivy image --input image.tar          # a saved archive, no daemon needed
trivy fs <dir|lockfile>                # software composition analysis
trivy repo <url|path> [--branch|--commit|--tag X]
trivy config <dir>                     # IaC and Dockerfile misconfiguration
trivy sbom <cyclonedx|spdx file>       # vuln by default; add license with --scanners
trivy image --format cyclonedx --output sbom.cdx.json <ref>
trivy image --exit-code 1 --severity HIGH,CRITICAL <ref>
trivy server --listen <addr> --token <t>   # one DB for many clients
trivy image --server http://<host>:4954 --token <t> <ref>
```
- **Image sources.** `image` tries the Docker engine, then containerd, then
  Podman, then the remote registry. `DOCKER_HOST` and `CONTAINERD_ADDRESS`
  point at other sockets. A reference found in none of them fails the scan.
- **Exit code.** Upstream: "By default, Trivy exits with code 0 even when
  security issues are detected." `--exit-code N` sets the code for findings,
  and `--severity` narrows both the report and that decision.
  `--exit-on-eol N` fails when the scanned OS is end of life.
- **Output.** `--format table|json|template|sarif|cyclonedx|spdx|spdx-json|github|cosign-vuln`
  with `--output <file>`. The JSON carries `SchemaVersion`, `ArtifactName`,
  `ArtifactType`, `Metadata` and `Results[]`; each vulnerability has
  `VulnerabilityID`, `PkgName`, `InstalledVersion`, `FixedVersion`, `Status`,
  `Severity` and a PURL. Within one `SchemaVersion`, optional fields may be
  added or left out (`FixedVersion` is absent when no fix exists), so a
  consumer ignores unknown fields and assumes no optional one.
- **Filtering.** `--ignore-unfixed` keeps only fixable findings;
  `--ignore-status <list>` drops by status; `--pkg-types os|library` limits the
  inventory; `--skip-files` and `--skip-dirs` take doublestar globs (also
  `scan.skip-files`, `scan.skip-dirs`).
- **Ignore files.** `.trivyignore` holds one ID per line (CVE, misconfiguration
  ID, secret rule or licence name), `#` comments and an optional
  `exp:YYYY-MM-DD` expiry, read from the working directory unless
  `--ignorefile` says otherwise. `.trivyignore.yaml` is **experimental**: it is
  read only when passed through `--ignorefile`, and scopes each entry by
  `paths`, `purls` (vulnerabilities only) and `expired_at`, with a `statement`
  that is a reason and does not filter. A Rego policy (`--ignore-policy`,
  package `trivy`, rule `ignore`) is experimental too.
- **Dev dependencies.** npm and yarn dev dependencies are left out unless
  `--include-dev-deps` is passed (npm, yarn and gradle support it).
- **Secret scanning.** On by default for `image` and `fs`; built-in rules over
  plaintext files (compiled Python included). `trivy-secret.yaml` in the
  current directory (or `--secret-config`) adds `rules`, `allow-rules`,
  `enable-builtin-rules`, `disable-rules` (which beats enable) and
  `skip-patterns`. Markdown is skipped by a built-in allow rule, and default
  skip patterns cover `.git`, `node_modules`, lockfiles, images and archives.
- **Misconfiguration in images** is "supported, but not useful in most cases";
  enable `--scanners misconfig` only when the image ships IaC files. Observed
  in practice: `trivy config` also parsed a Compose file, which the upstream
  IaC list does not name.

## VEX (experimental)
- `--vex` takes `repo` (a VEX repository), a local file, `oci` (an attestation
  in the registry) or `sbom-ref`; several can be combined, in priority order. A
  matched statement is logged at INFO as "Filtered out the detected
  vulnerability" and the finding leaves the report.
- **Formats.** OpenVEX and CSAF work for every target. CycloneDX VEX works only
  as a separate VEX BOM against a CycloneDX SBOM scan
  (`trivy sbom <sbom> --vex <vex>`), with `affects.ref` a BOM-Link
  (`urn:cdx:<serial>/<version>#<bom-ref>`). Observed in practice: passing a
  CycloneDX VEX to `image` or `fs` aborted the scan with no report; upstream
  states only the SBOM requirement, not the failure mode.
- **Id and PURL matching.** The vulnerability id is matched as a string, so in
  OpenVEX and CycloneDX a GHSA id suppresses like a CVE id (CSAF matches only
  its `cve` field), and only a not-affected or fixed status filters (OpenVEX
  `not_affected`, `fixed`; CycloneDX also `false_positive`, `resolved`). A product PURL with no version matches every version, and one with no
  qualifiers matches any qualifiers, so one statement can cover a package in
  every target. Observed in practice, a `cargo` PURL matched like the common
  types. A home-made VEX validator that admits only `CVE-` ids or a short list
  of PURL types is therefore the block, not Trivy: widen the validator, not the
  scanner. When the DB later reports a CVE id for a finding that a GHSA
  statement covered, the statement stops matching and the finding returns,
  which is the safe direction.
- **Scope.** A product with no subcomponents suppresses the CVE everywhere it
  is reached through that product (Trivy walks the dependency graph); listing
  the package as a subcomponent narrows the statement to it. A root that
  reaches the vulnerable module through several paths stays affected until
  every path is covered. A Go project as product, with the module as
  subcomponent, applies to every image that holds the binary.
- **OCI products.** `pkg:oci/<name>?repository_url=<repo>` applies to all tags
  of the image; adding `@sha256:<digest>` pins one digest. Observed in
  practice: matching against a locally built image with no repository digest
  failed; upstream says the digest is optional.
- `--show-suppressed` lists suppressed findings, exported in JSON as
  `ExperimentalModifiedFindings`. Trivy consumes VEX documents; it does not
  write them.

## Idioms & best practices
- **Gate deliberately.** Set `--exit-code` and `--severity` explicitly; the
  defaults pass every scan.
- **Download once, scan many.** Fetch the DB once (`--download-db-only`), then
  run each target with `--skip-db-update`, or run `trivy server` and point
  clients at it with `--server`.
- **Separate caches under parallelism.** Give concurrent runs separate
  `--cache-dir` paths, `--cache-backend memory`, or a shared Redis backend.
- **Record DB provenance.** `db/metadata.json` exists in the cache. Observed in
  practice: its `UpdatedAt` and `NextUpdate` timestamps, written into every
  report artifact, let a reviewer reject a scan made with a stale DB (upstream
  documents the file, not those fields).
- **Never apply VEX to the SBOM-generation run.** The SBOM stays the
  unsuppressed inventory; VEX applies in a later scan of it. (Observed in
  practice; consistent with the documented flow.)
- **Scan an immutable reference.** Scan by digest or pinned tag, and re-scan and
  diff when the scanner version moves: scan results are outside upstream's
  compatibility policy.
- **Run the container as the caller.** Observed in practice: the image runs as
  root, so a mounted cache and reports end up root-owned and a non-root
  cleanup step fails; pass `--user uid:gid`.
- Turn off what a job does not need (`--scanners vuln`, secret rule sets, skip
  patterns) for speed, knowing what each switch stops covering.

## General pitfalls
- **Exit 0 with findings** is the default.
- **Fatal errors and findings may share an exit code.** Observed in practice: a
  cache lock, a failed DB download or an unsupported VEX input ended the run
  with exit 1, so `--exit-code 1` cannot tell "found" from "crashed". Upstream
  documents only 0 and N. Use a value other than 1, or gate on the report.
- **Gate on the report, not on the exit.** Observed in practice: a report left
  by a previous run in a persistent output directory passes a presence check
  with old numbers. Check that it exists, parses and was written by this run;
  otherwise fail closed and record the counts as unknown, never 0.
- **BoltDB lock errors.** Concurrent processes sharing one filesystem scan
  cache hang or fail on the file lock; the read-only vulnerability DB is not
  the cause. A green re-run does not fix it. Two servers on one cache conflict
  the same way.
- **Stale DB under-reports silently.** A scan with `--skip-db-update` or an
  old default cache reports against whatever DB is there.
- **Skipped build output.** `--skip-dirs` over `dist`, `build`, `bin` or `obj`
  removes the shipped artifact from the scan.
- **Image source surprises.** A name present only on another engine, or a
  socket not mounted into the scanner container, makes `image` fail or fall
  through to a registry image of the same name (observed in practice; upstream
  documents the source order).
- **`--scanners vuln` drops secret scanning**, and the secret scanner reads the
  files in the target, not git history (upstream describes files only), so it
  does not replace a history scanner such as gitleaks.
- **Severity filters totals.** "Zero at MEDIUM+" is not "no findings".
- **Java scans are slow** and may need `--timeout 15m`; they can hit Maven
  Central 429s (pre-populate `~/.m2`, use a mirror, or `--offline-scan`, which
  skips missing POMs silently and can under-report).
- **Rate limits.** `GITHUB_TOKEN` helps only the VEX repository API, not DB
  downloads; mirror the DB with `--db-repository`.
- **A misplaced config key is not an error.** Observed in practice: a key under
  the wrong group in `trivy.yaml` was silently ignored; validate against the
  upstream schema.
- Remote `repo` scans clone under `/tmp`; a dirty repository bypasses the scan
  cache.

## Testing
Upstream gives consumers no test guidance; it documents each filter with an
example against a public image and shows the "Filtered out" log line and the
`--show-suppressed` table as evidence. The shapes below were observed in
practice:
- treat a VEX or config file passed on the command line as not yet applied:
  give every input file (VEX, ignore file, config) an offline acceptance test,
  run with the pinned scanner version, in which the scanner accepts the file and
  a planted finding must be suppressed and must appear under
  `--show-suppressed`, and record a statement as applied only when
  `--show-suppressed` lists what it filtered;
- assert the gate fails on a fixture image or lockfile with a known finding,
  and that a missing or unparsable report fails the job;
- keep a scan of a known target as a canary when the scanner version moves, and
  diff the result.

## Security defaults
- `trivy server` listens on `localhost:4954` by default. The token is optional
  (header `Trivy-Token`), the protocol is plain HTTP, `/healthz` and `/version`
  need no token, and there is no per-client permission or tenant isolation.
  Put it behind a TLS proxy, restrict the network, and run separate servers for
  clients that must not see each other's uploads.
- In client/server mode clients analyze locally and upload package lists;
  secret findings are masked before upload.
- Registry access: `--username`, `--password-stdin`, `--cacert`.
  `--insecure` (or `TRIVY_INSECURE`) turns TLS verification off.
- Mounting the engine socket into the scanner container gives it full engine
  control; mount it only where image scanning needs it.
- Reports name every vulnerable package and any secret found; treat them as
  sensitive build output.

## Operational behaviour
- Startup fetches any DB it lacks (and checks for updates unless skipped); an
  offline host needs the DB files copied into `db/` and `java-db/` and the skip
  flags set.
- Resource knobs: `--parallel` (goroutines), `--timeout`; `--no-progress` and
  `--quiet` for CI logs.
- Cache backends (experimental flag): `fs` is the default for image, VM and
  repository scans, `memory` for `fs`, `rootfs`, `config` and `sbom`, and
  `redis://` (with `--redis-tls`, `--redis-ca`, `--redis-cert`, `--redis-key`)
  shares one cache across instances. Memory and Redis do not lock.
- Each CLI version reads specific DB schema versions; an old CLI stops getting
  new data when its schema is retired. Client and server versions are not
  guaranteed compatible, so upgrade them together.

## Interop
- Official ecosystem: the `trivy-action` GitHub Action, a Kubernetes operator
  and an editor extension.
- Writes SARIF (code-scanning upload), CycloneDX and SPDX SBOMs, a GitHub
  dependency snapshot and templated output.
- Reads CycloneDX, SPDX and KBOM SBOMs, OpenVEX, CSAF and CycloneDX VEX, and
  Cosign-produced OCI attestations.
- Engines: Docker Engine, containerd (experimental) and Podman, or a remote
  registry directly. The engine page is
  [`container/docker.md`](../container/docker.md).
- A history secret scanner complements it:
  [`cli/gitleaks.md`](gitleaks.md).

## Major lines
Trivy is a 0.x project, so there is no major line to section. Upstream's
compatibility policy names the stable interfaces (commands, flags, config keys,
environment variables, exit codes, machine-readable formats) and leaves out
scan results, terminal layout, DB and cache formats, client/server pairing and
experimental features (VEX, `.trivyignore.yaml`, `--show-suppressed`, cache
backends, Rego ignore). Breaking changes land in minor releases and are marked
in the release notes, so read them at every scanner bump. The old
`--skip-update` flag is now `--skip-db-update`, and DB schema v1 is long
retired.

## Upstream docs
- https://trivy.dev/docs/latest/ (source: https://github.com/aquasecurity/trivy/tree/main/docs)
- https://trivy.dev/docs/latest/guide/configuration/
- https://trivy.dev/docs/latest/guide/configuration/filtering/
- https://trivy.dev/docs/latest/guide/configuration/db/
- https://trivy.dev/docs/latest/guide/configuration/cache/
- https://trivy.dev/docs/latest/guide/supply-chain/vex/
- https://trivy.dev/docs/latest/guide/references/modes/client-server/
- https://trivy.dev/docs/latest/guide/references/troubleshooting/
- https://trivy.dev/docs/latest/guide/references/compatibility/
- https://github.com/aquasecurity/trivy
