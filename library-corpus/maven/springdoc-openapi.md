# springdoc-openapi — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A library that generates OpenAPI (Swagger) documentation for a Spring
application by introspecting its controllers, request/response models, and
annotations at runtime. It also serves an interactive Swagger-UI page so the
API can be browsed and exercised from the browser. The coordinates differ by
major line, so they are not interchangeable spellings:
`org.springdoc:springdoc-openapi-ui` is the 1.x line (Spring Boot 2, `javax`)
only, and the `org.springdoc:springdoc-openapi-starter-*` family (a
WebMVC/WebFlux variant, with or without the bundled UI) is 2.x and later
(Spring Boot 3 and up). Moving from 1.x to 2.x is a coordinate change. The
starters are `org.springdoc:springdoc-openapi-starter-webmvc-ui` and
`org.springdoc:springdoc-openapi-starter-webflux-ui` (document plus UI) and
`org.springdoc:springdoc-openapi-starter-webmvc-api` (document only).

## Install, setup and configuration
- Pick the starter that matches the web stack: `-webmvc-*` for servlet
  applications, `-webflux-*` for reactive ones; `-api` when no UI is wanted.
- It is auto-configured from the class path: there is no enable annotation, and
  a springfox `Docket` bean does nothing here.
- Spring Boot's BOM does not manage it: every POM names a version. The project
  publishes its own BOM on later 2.x releases and after. Centralize the version
  in a shared parent property, or drift between services stays invisible until
  every POM is read (observed in practice).
- **Default endpoints:** `/v3/api-docs` (JSON), `/v3/api-docs.yaml`, and
  `/swagger-ui.html`, which redirects to `/swagger-ui/index.html`, plus the UI
  assets. The servlet context path prefixes all of them;
  `springdoc.api-docs.path` and `springdoc.swagger-ui.path` move them.
- **Switches:** `springdoc.api-docs.enabled` (default true) turns off the
  document endpoint and, per the FAQ, all of springdoc's auto-configuration;
  `springdoc.swagger-ui.enabled` (default true) turns off only the UI.
  `springdoc.packages-to-scan` and `springdoc.paths-to-match` narrow what is
  documented.
- Behind a reverse proxy, forward headers decide the server URL the UI shows;
  the FAQ covers the setup.

## Core API / usage shape
- Adding the dependency is most of the setup: at runtime it scans the mapped
  endpoints and exposes a generated OpenAPI document (a JSON/YAML endpoint) plus
  a Swagger-UI page, without hand-written spec files.
- The generated spec is enriched with annotations on controllers and models
  (`@Operation`, `@ApiResponse`, `@Parameter`, `@Tag`, `@Schema`), which add
  summaries, descriptions, examples, and constraints the introspector cannot
  infer on its own.
- Global metadata (title, description, version label, contact, security schemes,
  servers) is customized by declaring an `OpenAPI` bean, rather than editing a
  static document.
- The annotations and model types (`@Operation`, `@Tag`, `@Schema`, `OpenAPI`,
  `SecurityScheme`) come from swagger-core (`io.swagger.v3.oas.*`), not from
  springdoc, so an `OpenAPI` bean usually survives a line change untouched.
  springdoc's own classes did move between 1.x and 2.x; Major lines lists the
  moves.
- `GroupedOpenApi` beans define documentation groups (one document per group).
  A `SecurityScheme` of type HTTP `bearer` on the `OpenAPI` bean, or the
  `@SecurityScheme` annotation, gives the UI an Authorize button.
- `springdoc.swagger-ui.urls` lists several documents in one UI, for example
  one per routed service behind a gateway.

## Idioms & best practices
- Treat the generated document as derived from the code: annotate the
  controllers and DTOs so the spec stays accurate as the API changes, instead of
  maintaining a separate hand-authored spec that drifts.
- Use an `OpenAPI` bean for cross-cutting metadata and security-scheme
  definitions; use per-endpoint annotations only for what is local to that
  operation.
- Give the document a consumer: a generated client, a contract test, or a spec
  diff in CI. A document nobody consumes guarantees nothing about client/server
  agreement, and drift costs nothing (observed in practice).

## General pitfalls
- springdoc and the Swagger-2-era [`springfox`](./springfox.md) are two
  DISTINCT, non-interoperable toolchains that solve the same problem. Do not mix
  them in one codebase: their annotations, configuration, and generated
  endpoints conflict. Pick one and remove the other.
- The UI and the machine-readable spec are exposed as HTTP endpoints; be
  deliberate about whether they should be reachable in every environment, and
  secure or disable them where they should not be public.
- **Turning off the UI leaves the document.** `springdoc.swagger-ui.enabled=false`
  hides only the UI; production that must not publish the API description also
  needs `springdoc.api-docs.enabled=false`. Prefer turning the document off
  (404) to authenticating it where nothing consumes it: a 401 path still hands
  the full operation map to any authenticated user. When checking an edge for
  exposure, request a known-bogus path beside each document path, because an
  SPA catch-all answers both with 200 and the same body, and neither result
  then shows a leak (the review procedure is
  [`fleet-security-review`](../../skill-corpus/fleet-security-review.md), and
  the unrouted-path control is in
  [`http-smoke-suite`](../../tool-corpus/testing/http-smoke-suite.md)).
- **Allow-lists follow the paths.** Security allow-list entries are written
  against one line's default paths; after a line change, or a move from
  springfox, re-check them against the paths actually served. A stale springfox
  allow-list makes the UI answer 401 (observed in practice).
- When overriding Boot's `HttpMessageConverter`s, keep a
  `ByteArrayHttpMessageConverter` registered, or the UI cannot render the
  document (FAQ).

## Testing
- Fetch `/v3/api-docs` in an integration test and compare it with a committed
  copy, or feed it to a contract or client-generation step: this turns the
  generated document into a checked artifact. Upstream documents the endpoint;
  the test practice is advice.

## Security defaults
- Both endpoints are on by default and are not protected by springdoc itself;
  whatever the application's security chain allows decides who reads them.
  Authorize-button support documents the API's own scheme and grants nothing.

## Operational behaviour
- The document is generated by introspecting the running application, so it
  reflects the mappings actually registered. Declaring
  `@OpenAPIDefinition` and `@SecurityScheme` on a Spring-managed bean speeds up
  generation (upstream advice).

## Interop
- [`spring-boot`](./spring-boot.md) and the web stack decide the starter.
- [`spring-security`](./spring-security.md): permit `/v3/api-docs/**`,
  `/swagger-ui/**` and `/swagger-ui.html` explicitly when the UI is public.
- [`springfox`](./springfox.md): the migration map from springfox lives there.
- [`jackson`](./jackson.md): springdoc gets its document mapper from its own
  `ObjectMapperProvider` bean, which the FAQ's minimal-bean setup declares. The
  fetched pages do not say how that mapper relates to the application's own.

## Major lines
### 1.x (Spring Boot 2)
`org.springdoc:springdoc-openapi-ui` and its siblings, `javax` namespace.

### 2.x (Spring Boot 3)
The `springdoc-openapi-starter-*` coordinates. Moving from 1.x replaces
`springdoc-openapi-ui` with `springdoc-openapi-starter-webmvc-ui`. The
`-data-rest`, `-security`, `-kotlin`, `-javadoc`, `-hateoas` and `-groovy`
modules fold into `springdoc-openapi-starter-common` and are removed from the
build. Classes move too:
- `org.springdoc.core.GroupedOpenApi` to `org.springdoc.core.models.GroupedOpenApi`;
- `org.springdoc.api.annotations.ParameterObject` to
  `org.springdoc.core.annotations.ParameterObject`;
- `OpenApiCustomiser` to `OpenApiCustomizer` (same package,
  `org.springdoc.core.customizers`);
- `SpringDocUtils` and `Constants` to `org.springdoc.core.utils`;
- `SwaggerUiConfigParameters` to `org.springdoc.core.properties`.

### 3.x (Spring Boot 4)
The same starter artifact ids as 2.x; moving from 2.x is a version change. The
compatibility matrix in the FAQ pairs 3.x with Boot 4.

## Upstream docs
- https://springdoc.org/
- https://springdoc.org/properties.html
- https://springdoc.org/faq.html
- https://springdoc.org/migrating-from-springdoc-v1.html
- https://springdoc.org/migrating-from-springfox.html
- https://github.com/springdoc/springdoc-openapi
- https://swagger.io/specification/
