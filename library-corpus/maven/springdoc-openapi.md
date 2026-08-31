# springdoc-openapi — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
A library that generates OpenAPI (Swagger) documentation for a Spring
application by introspecting its controllers, request/response models, and
annotations at runtime. It also serves an interactive Swagger-UI page so the
API can be browsed and exercised from the browser. It is published both as
`org.springdoc:springdoc-openapi-ui` and as the
`org.springdoc:springdoc-openapi-starter-*` starter family (a WebMVC/WebFlux
variant, with or without the bundled UI).

## Core API / usage shape
- Adding the dependency is most of the setup: at runtime it scans the mapped
  endpoints and exposes a generated OpenAPI document (a JSON/YAML endpoint) plus
  a Swagger-UI page, without hand-written spec files.
- The generated spec is enriched with annotations on controllers and models —
  `@Operation`, `@ApiResponse`, `@Parameter`, `@Tag`, `@Schema` — which add
  summaries, descriptions, examples, and constraints the introspector cannot
  infer on its own.
- Global metadata (title, description, version label, contact, security schemes,
  servers) is customized by declaring an `OpenAPI` bean, rather than editing a
  static document.

## Idioms & best practices
- Treat the generated document as derived from the code: annotate the
  controllers and DTOs so the spec stays accurate as the API changes, instead of
  maintaining a separate hand-authored spec that drifts.
- Use an `OpenAPI` bean for cross-cutting metadata and security-scheme
  definitions; use per-endpoint annotations only for what is local to that
  operation.

## General pitfalls
- springdoc and the Swagger-2-era [`springfox`](./springfox.md) are two
  DISTINCT, non-interoperable toolchains that solve the same problem. Do not mix
  them in one codebase — their annotations, configuration, and generated
  endpoints conflict. Pick one and remove the other.
- The UI and the machine-readable spec are exposed as HTTP endpoints; be
  deliberate about whether they should be reachable in every environment, and
  secure or disable them where they should not be public.

## Upstream docs
- https://springdoc.org/
- https://github.com/springdoc/springdoc-openapi
- https://swagger.io/specification/
