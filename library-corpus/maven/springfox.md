# springfox — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A Swagger-2-era API-documentation generator for Spring MVC, predating OpenAPI 3.
It scans MVC controllers and emits a Swagger/OpenAPI document plus an
interactive UI.

**Springfox is superseded.** The OpenAPI-3 generator described in
[`springdoc-openapi.md`](./springdoc-openapi.md) is where new API-documentation
work goes; this page exists to orient someone maintaining or retiring an
existing Springfox setup, never to start one.

## Core API / usage shape
- **Annotation/config-driven scanning**: configuration and annotations drive a
  scan of the Spring MVC controllers, from which Springfox emits a
  Swagger/OpenAPI document and serves a browsable UI.
- Setup is centered on enabling the scan and declaring the document metadata via
  configuration beans.

## Idioms & best practices
- Exactly one API-doc generator per codebase. The two toolchains are
  non-interoperable and conflict on a shared classpath —
  [`springdoc-openapi.md`](./springdoc-openapi.md) owns that rule.

## General pitfalls
- **Swagger-2-era output.** Documents it produces have feature and
  spec-coverage gaps relative to OpenAPI-3 generators and cannot carry
  OpenAPI-3-only constructs.
- **Path/request-matching incompatibilities.** It has known path-matching and
  request-matching incompatibilities across major Spring MVC / Spring Boot lines,
  which can break startup or documentation scanning after a framework upgrade.
- **Half-staged retirement is the common state.** A frequent transitional shape
  is the dependency being present but unwired, or both generators sitting on the
  classpath at once. Verify which generator is actually active before assuming
  the changeover is complete.

## Upstream docs
- https://springfox.github.io/springfox/
- https://github.com/springfox/springfox
