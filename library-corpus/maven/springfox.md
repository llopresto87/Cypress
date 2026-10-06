# springfox — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A Swagger-2-era API-documentation generator for Spring MVC, predating OpenAPI 3.
It scans MVC controllers and emits a Swagger/OpenAPI document plus an
interactive UI. Coordinates by generation: 2.x is
`io.springfox:springfox-swagger2` plus `io.springfox:springfox-swagger-ui`,
switched on with `@EnableSwagger2`; the 3 line is
`io.springfox:springfox-boot-starter`, auto-configured. Its one release is the
last springfox release published to Maven Central, and it targets the `javax` (Spring Boot 2)
world. Home: https://github.com/springfox/springfox.

**Springfox is superseded.** The OpenAPI-3 generator described in
[`springdoc-openapi.md`](./springdoc-openapi.md) is where new API-documentation
work goes; this page exists to orient someone maintaining or retiring an
existing Springfox setup, never to start one.

## Install, setup and configuration
- 2.x: add both artifacts, annotate a configuration class with
  `@EnableSwagger2`, and declare `Docket(DocumentationType.SWAGGER_2)` beans.
- The 3 line on Spring Boot: replace the 2.x artifacts with `springfox-boot-starter`
  and remove `@EnableSwagger2`; plain Spring MVC uses `@EnableOpenApi` and the
  `springfox-oas` library. 3.x dropped Guava, so Guava predicates in `Docket`
  selectors become Java functional interfaces.
- Default paths. The Swagger 2 document is served at `/v2/api-docs`, one group
  per `Docket` via `?group=<groupName>`, and
  `springfox.documentation.swagger.v2.path` overrides the path.
  `/swagger-resources` lists the documents the UI offers. The UI is at
  `/swagger-ui.html` on 2.x and moved to `/swagger-ui/index.html` (or
  `/swagger-ui/`) with `springfox-boot-starter`. The fetched docs do not give
  the default path of the OpenAPI 3 document.

## Core API / usage shape
- **Annotation/config-driven scanning**: configuration and annotations drive a
  scan of the Spring MVC controllers, from which Springfox emits a
  Swagger/OpenAPI document and serves a browsable UI.
- Setup is centered on enabling the scan and declaring the document metadata via
  configuration beans.
- `Docket` beans select APIs and paths (`RequestHandlerSelectors`,
  `PathSelectors`) and name groups; `ApiKey`, `SecurityContext` and
  `SecurityReference` describe authentication; Swagger-2 annotations
  (`@Api`, `@ApiOperation`, `@ApiParam`, `@ApiModel`, `@ApiModelProperty`)
  describe operations and models.
- `SwaggerResourcesProvider` is the extension point that lists the documents
  the UI offers; a gateway can implement it to list each routed service's
  document, including OpenAPI-3 documents served by springdoc.

## Idioms & best practices
- Exactly one API-doc generator per codebase. The two toolchains are
  non-interoperable and conflict on a shared classpath —
  [`springdoc-openapi.md`](./springdoc-openapi.md) owns that rule.
- Retire it by migrating to springdoc, using springdoc's own map:
  remove springfox and the Swagger-2 annotations; `@Api` → `@Tag`;
  `@ApiIgnore` → `@Parameter(hidden = true)`, `@Operation(hidden = true)` or
  `@Hidden`; `@ApiImplicitParam` → `@Parameter`; `@ApiModel` and
  `@ApiModelProperty` → `@Schema`; `@ApiOperation(value, notes)` →
  `@Operation(summary, description)`; `@ApiParam` → `@Parameter`;
  `@ApiResponse(code, message)` → `@ApiResponse(responseCode, description)`;
  several `Docket` beans → `GroupedOpenApi` beans, a single `Docket` →
  `springdoc.packagesToScan` / `springdoc.pathsToMatch` properties plus an
  `OpenAPI` bean. `ApiKey` / `SecurityContext` become a `SecurityScheme` and a
  `SecurityRequirement`, and security allow-list paths change.
- A gateway that aggregates documents through `SwaggerResourcesProvider` exits
  through springdoc's multi-document UI (`springdoc.swagger-ui.urls`), not
  through a springfox upgrade.

## General pitfalls
- **Swagger-2-era output.** Documents it produces have feature and
  spec-coverage gaps relative to OpenAPI-3 generators and cannot carry
  OpenAPI-3-only constructs.
- **Path/request-matching incompatibilities.** It has known path-matching and
  request-matching incompatibilities across major Spring MVC / Spring Boot lines,
  which can break startup or documentation scanning after a framework upgrade.
  The named case: late in the Boot 2 line the default MVC matcher became
  `PathPatternParser`, and springfox then fails at start-up. Observed in
  practice, the failure is a `NullPointerException` in
  `documentationPluginsBootstrapper`, and the workaround
  `spring.mvc.pathmatch.matching-strategy=ant-path-matcher` does not cover
  Actuator endpoints, so an application with Actuator can still fail. The Boot
  release notes document the matcher change, not the springfox failure.
- **Half-staged retirement is the common state.** A frequent transitional shape
  is the dependency being present but unwired, or both generators sitting on the
  classpath at once. Verify which generator is actually active before assuming
  the changeover is complete. Read the resolved class path
  (`mvn dependency:tree`), not the POM text: a commented-out springdoc
  dependency beside a live springfox one is the usual sign.
- **Reflective fixes.** A plugin that reaches into springfox's private fields
  with `setAccessible` to survive a framework upgrade signals a version
  mismatch, and breaks under the JDK's strong encapsulation (observed in
  practice; see [`java`](../language/java.md)).
- **An old bundled UI.** Old springfox lines bundle an old swagger-ui webjar
  with known client-side advisories; removing springfox closes that surface
  and springdoc keeps the UI feature (observed in practice).

## Testing
- Upstream documents no springfox-specific test support. A test that starts the
  full application context proves the scan still starts after a framework
  change, because the known failures above are start-up failures.

## Security defaults
- The UI and document endpoints are public unless the application's security
  chain protects them; springfox adds no protection of its own. Since no release
  will follow the 3 line, any advisory against its bundled dependencies stays open
  until springfox is removed.

## Operational behaviour
- The scan runs at application start-up, which is why a matching-strategy
  incompatibility fails the whole start rather than one endpoint.

## Interop
- [`springdoc-openapi`](./springdoc-openapi.md): the successor and migration
  target.
- [`spring-boot`](./spring-boot.md): springfox works on the Boot 2 line only;
  Boot 3 (Jakarta) has no springfox release.
- [`spring-security`](./spring-security.md): allow-list entries for the
  documentation paths change on migration.

## Major lines
### 2.x
`springfox-swagger2` and `springfox-swagger-ui`, `@EnableSwagger2`, Swagger 2
documents, Guava predicates in selectors.

### 3.x
`springfox-boot-starter`, auto-configured on Boot; OpenAPI 3 support beside
Swagger 2; Guava removed. The terminal release.

## Upstream docs
- https://springfox.github.io/springfox/
- https://springfox.github.io/springfox/docs/current/
- https://github.com/springfox/springfox
- https://repo1.maven.org/maven2/io/springfox/springfox-boot-starter/maven-metadata.xml (release list)
- https://springdoc.org/migrating-from-springfox.html
