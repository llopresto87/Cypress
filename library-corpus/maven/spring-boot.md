# spring-boot — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
An opinionated JVM application framework that stands up production-ready Spring
applications with minimal configuration. It provides auto-configuration (beans
are wired based on what is on the classpath), a curated starter-dependency BOM,
an embedded servlet container so an app runs as a self-contained executable jar,
and Actuator for production operations. Canonical coordinates:
`org.springframework.boot:spring-boot-starter-parent` as the parent POM (or the
`spring-boot-dependencies` BOM imported in `dependencyManagement`), plus
`spring-boot-starter-*` modules (e.g. `spring-boot-starter-web`,
`spring-boot-starter-actuator`) for each capability. It sits on
[`spring-framework`](./spring-framework.md), whose version its BOM supplies.

Support policy (open-source): a major line is supported for up to three years
and each minor release for at least twelve months, and you must be on a
supported minor to get fixes, so stopping on an old minor ages out of support
however young the major is. Commercial support runs longer, and only the last
minor of each major gets the extended enterprise period. Exact end dates live on
https://spring.io/projects/spring-boot#support, not here.

## Install, setup and configuration
- **Parent or BOM.** The starter parent gives managed versions, plugin
  management, `maven.compiler.release` from `<java.version>`, and the
  `-parameters` compiler flag. An imported `spring-boot-dependencies` BOM gives
  versions only; overriding a managed version then needs a
  `<dependencyManagement>` entry before the import, because version properties
  work only through the parent (the mechanism is on [`maven`](../cli/maven.md)).
- **Starters carry no `<version>`.** A version on a Boot starter means something
  is working around the parent; find out why before copying it (observed in
  practice).
- **Externalized configuration** is layered and later sources override earlier
  ones: packaged `application.properties` / `application.yml`, then
  profile-specific files, environment variables, Java system properties and
  command-line arguments, among others (the reference lists the full order).
  `SPRING_APPLICATION_JSON` supplies inline JSON through an environment
  variable or system property. Relaxed binding maps an environment variable such
  as `MANAGEMENT_TRACING_ENABLED` onto `management.tracing.enabled`; refer to
  properties in their canonical kebab-case form.
- **Imports.** `spring.config.import` pulls in further sources; `optional:`
  lets the application start when a location is missing, and `configtree:`
  reads a directory of mounted files as properties. The legacy `bootstrap.yml`
  belongs to Spring Cloud; see [`spring-cloud`](./spring-cloud.md).
- **Profiles.** `spring.profiles.active`, `spring.profiles.default` and
  `spring.profiles.include` may appear only in non-profile-specific documents,
  never in an `application-<profile>.yml` or a document activated by
  `spring.config.activate.on-profile`.
- **Typed configuration.** `@ConfigurationProperties` gives type safety,
  `@Validated` validation, relaxed binding and IDE metadata. Records bind
  through their constructor with no extra annotation (unless the record has
  several constructors), and `@ConfigurationPropertiesScan` registers the
  classes in bulk. Constructor binding needs classes compiled with
  `-parameters`; the starter parent and Boot's Gradle plugin set it, a build that
  imports the BOM must set it itself.
- **Database initialization.** `spring.sql.init.mode` decides whether
  `schema.sql` and `data.sql` run: by default only for an embedded in-memory
  database (H2, HSQLDB, Derby), never for MySQL or Postgres unless set to
  `always` (`never` disables it). So a seed script that creates the first
  account never reaches a production database, and with self-registration off
  nobody can log in. Before switching to `always`, which runs the scripts on
  every start, make them idempotent (no fixed ids that collide on the second
  run), or seed the first account through the migration tool. Script
  initialization runs before JPA schema creation; set
  `spring.jpa.defer-datasource-initialization=true` for scripts that build on
  Hibernate's DDL. See [`h2`](./h2.md).

## Core API / usage shape
- An application class annotated `@SpringBootApplication` (which composes
  `@Configuration`, `@EnableAutoConfiguration`, and `@ComponentScan`) launched
  via `SpringApplication.run(...)`.
- Starters are dependency aggregates: adding one starter pulls the whole,
  version-aligned set of libraries for a capability rather than listing each
  transitively.
- Auto-configuration classes back off when the developer supplies their own bean
  (conditional configuration), so defaults are overridable by declaring a
  competing bean.
- **The auto-configuration report** says what was applied and why: start with
  `--debug` (or `debug=true`) to log the conditions report, or read the
  `conditions` Actuator endpoint.
- Externalized configuration is layered (property/YAML files, environment
  variables, command-line args, profiles) and bound into typed configuration
  objects.
- **Actuator endpoints** include `health`, `info`, `conditions`, `beans`,
  `configprops`, `env`, `mappings`, `loggers`, `metrics`, `heapdump` and
  others; `livenessstate` and `readinessstate` health indicators back the
  liveness and readiness probe groups.

## Idioms & best practices
- Import the starter-parent or the BOM once so transitive dependency versions
  are aligned across an entire fleet of services (BOM-driven version alignment);
  avoid pinning individual Spring/third-party versions that the BOM already
  governs.
- Prefer a starter over hand-assembling its constituent dependencies; let
  auto-configuration wire the defaults and override only the specific beans you
  need to change.
- Use Actuator as the standard mechanism for exposing health, readiness, and
  metrics endpoints; it integrates with Micrometer to publish to external
  metrics/monitoring registries.
- Use profiles and externalized configuration for per-environment differences
  rather than branching in code.
- Prefer `@ConfigurationProperties` over scattered `@Value`, and constructor
  injection (`final` fields, one constructor, no `@Autowired`) over field
  injection.
- A version-property override on the parent (`<tomcat.version>` and the like)
  patches one managed library without moving the Boot line. Observed in
  practice: it silently regresses or overshoots when a later parent bump keeps
  it unexamined, so review every override at each parent bump.
- During an upgrade add `spring-boot-properties-migrator` (runtime scope): at
  start-up it reports renamed or removed keys and temporarily remaps them.
  Remove it once the migration is done.
- Keep secrets out of environment variables where you can: the reference says
  they "have drawbacks" for secrets and offers mounted configuration trees
  (`configtree:`) instead. Boot has no built-in property encryption.
- Run each service on its own parent and let the parent decide runtime
  versions: a library jar compiled against an older Boot runs on the
  *consuming* application's BOM classpath (observed in practice; it follows
  from Maven mediation).

## General pitfalls
- Auto-configuration is classpath-driven: adding or removing a dependency can
  silently change which beans get configured. When behavior appears "magic,"
  inspect the auto-configuration report rather than guessing.
- Actuator endpoints can expose sensitive operational detail; deliberately
  choose which endpoints are exposed and how they are secured rather than
  exposing everything.
- Overriding one auto-configured bean can disable a chain of related
  auto-configuration that depended on the default; verify the surrounding wiring
  still holds after a manual override.
- **Unknown property keys bind nothing and fail nothing** (observed in
  practice). A renamed key stays "configured", the service starts healthy, and
  it falls back to defaults, such as `localhost` for a datastore. A key whose
  deprecation level is `error` in `spring-configuration-metadata.json` binds
  nothing either. Audit renamed keys at every upgrade.
- **A profile with no backing document** (observed in practice). An active
  profile name that matches no `application-<profile>.yml` contributes nothing
  and reports nothing.
- **Exposure widening.** Over HTTP only `health` is exposed by default.
  Widening `management.endpoints.web.exposure.include` (worst case `'*'`)
  together with a security allow-list entry like `/actuator/**` publishes every
  enabled endpoint unauthenticated, and a later-added endpoint is published
  with no further step.
- **A custom `SecurityFilterChain` turns off Boot's actuator security.** With
  Spring Security present and no chain of your own, Boot secures every actuator
  except `/health`; once you define a chain, Boot backs off, and an app-wide
  `permitAll` then opens every exposed endpoint. A configuration flag that
  flips the whole chain to `permitAll` is covered on
  [`spring-security`](./spring-security.md).
- **A separate management port** (`management.server.port`) keeps Actuator off
  the application port, which the reference recommends for security. Boot runs
  that port as a child context and, when Spring Security is present, reuses the
  application's security filter chain there (Boot's source; the reference is
  silent), so the application's request matchers also decide what the
  management port answers. Liveness and scrape endpoints need their own narrow
  permit entries (`health`, `health/**`, `info`, `prometheus`, never
  `/actuator/**`), and a health-check carve-out removed on the theory that the
  chain does not reach that port turns every container health check into 401.
  Keep sensitive endpoints closed twice: left out of the exposure list (404)
  and not permitted (401). Probe the real port before changing either. The
  reference also warns that a separate port can make health checks unreliable.
- **An optional dependency can take the aggregate health down.** When mail is
  configured, its health indicator connects to the SMTP server, so a dead relay
  or credential turns `/actuator/health` DOWN and fails every container health
  check that reads it; `spring.mail.test-connection=true` makes the same
  failure stop start-up. Decide which dependencies the probe a platform reads
  should include: turn the mail indicator off
  (`management.health.mail.enabled=false`, the per-indicator switch) or move
  the probe to a health group that leaves it out, and record that the
  exclusion is deliberate.
- **Fat-jar resources.** Read class-path resources as streams; a jar entry is
  not a file (see [`spring-framework`](./spring-framework.md)).
- **DevTools** belongs in `optional` scope (Maven) or `developmentOnly`
  (Gradle). Boot's repackaging excludes it by default (`excludeDevtools`), and
  it turns itself off when the application runs fully packaged; packaging that
  bypasses Boot's plugin does not get the exclusion.
- **Multi-repository fleets** (observed in practice). With no shared parent,
  nothing makes two services on "the same" Boot line resolve the same versions;
  diff `dependency:tree` across them.
- **The declared parent is not the deployed version** (observed in practice).
  To answer "is fix X live", list the jars under `BOOT-INF/lib` of the running
  artifact, where `JarLauncher` loads them from.
- **Coordinate moves** drop a dependency out of BOM management; the MySQL driver
  moved to `com.mysql:mysql-connector-j` (see
  [`mysql-connector-j`](./mysql-connector-j.md)).

## Testing
- `@SpringBootTest` loads the full context. By default it starts no server
  (`webEnvironment = MOCK`); `RANDOM_PORT` and `DEFINED_PORT` start a real one.
- Test slices (`@WebMvcTest`, `@DataJpaTest` and the others) load only the beans
  one layer needs. A nested `@TestConfiguration` adds to the primary
  configuration instead of replacing it.
- `@MockitoBean` and `@MockitoSpyBean` (from Spring Framework) define mocks and
  spies in the context; Boot's own `@MockBean` and `@SpyBean` are gone on Boot 4.
- Testcontainers: `@ServiceConnection` on a container field wires the matching
  connection properties; `@DynamicPropertySource` is the more verbose,
  more flexible alternative. See [`testcontainers`](./testcontainers.md).
- Under `@SpringBootTest`, metrics registries other than the in-memory one are
  not auto-configured; add `@AutoConfigureMetrics` when a test needs them. The
  same holds for reporting tracing components; the annotation for each Boot line
  is on [`micrometer-tracing`](./micrometer-tracing.md).
- Wire a properties-migrator run and a renamed-key audit into upgrade work; a
  green test suite says nothing about keys that silently stopped binding.

## Security defaults
- HTTP exposure defaults to `health` only (JMX likewise).
- `management.endpoint.health.show-details` (and `show-components`) default to
  `never`; `when-authorized` needs an authorizing security chain on the port
  that serves Actuator, or it has nothing to authorize against.
- `env`, `configprops` and `quartz` values are always masked by default on
  Boot 3 and later (`show-values`: `never`, `when-authorized`, `always`). On
  Boot 2 only keys that looked sensitive (password, secret, key, token,
  credentials) were masked. Do not rely on masking: keep `env`, `configprops`
  and `heapdump` unexposed.
- With Spring Security on the class path and no chain of your own, every
  actuator except `/health` is secured.
- No built-in property encryption.

## Operational behaviour
- **Graceful shutdown** is on by default on current lines for Jetty, Reactor
  Netty and Tomcat: in-flight requests may finish, no new ones are accepted.
  Bound the wait with `spring.lifecycle.timeout-per-shutdown-phase`. Earlier
  lines needed `server.shutdown=graceful`. Shutdown from an IDE may be immediate.
- **Executable jars and containers.** `JarLauncher` loads nested jars from
  `BOOT-INF/lib/`. Running from an exploded directory is faster and recommended
  in production: `java -Djarmode=tools -jar app.jar extract` unpacks it, and the
  layered layout separates dependencies from application classes so an image
  rebuild reuses the dependency layers. Within the Boot 3 line the launcher
  classes moved to `org.springframework.boot.loader.launch`; scripts that name
  the old class must follow.
- Liveness and readiness health groups are on by default and can be served on
  the main or the management port.

## Interop
- [`spring-framework`](./spring-framework.md): Boot 3 runs Framework 6, Boot 4
  runs Framework 7.
- [`spring-cloud`](./spring-cloud.md): each Boot line pairs with a Cloud release
  train; keep the two matched.
- [`spring-security`](./spring-security.md): Boot's security auto-configuration
  and the actuator rules above.
- [`jackson`](./jackson.md): the default JSON engine and its customization.
- [`micrometer-tracing`](./micrometer-tracing.md) and
  [`sleuth-zipkin`](./sleuth-zipkin.md): tracing on Boot 3 and later, and before.
- [`maven`](../cli/maven.md) and [`java`](../language/java.md): build and
  language-level coupling.

## Major lines
### Boot 2
`javax.*`. Late in the 2 line, circular bean references became forbidden by
default (`spring.main.allow-circular-references` is the escape hatch; break the
cycle instead), and the default MVC path matcher changed from `AntPathMatcher`
to `PathPatternParser` (springfox breaks;
`spring.mvc.pathmatch.matching-strategy=ant-path-matcher` reverts it; Spring
Security `mvcMatchers` need a leading slash). The last 2 line introduced
`META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`
for registering auto-configuration.

### Boot 2 to Boot 3
Upgrade to the latest release of the last 2 line first. Then: Java 17 minimum;
`javax.*` becomes `jakarta.*` (a transitive `javax.servlet-api` can sneak back
in, so check `dependency:tree`, observed in practice); registration of
auto-configuration in `spring.factories` replaced by the `.imports` file;
trailing-slash matching off; Spring Security 6; Hibernate 6 (dialect and
id-generation changes, observed in practice); Actuator `env` / `configprops`
values masked by default; Spring Cloud Sleuth replaced by Micrometer Tracing.

### Boot 3 to Boot 4
Spring Framework 7 and still Java 17 or later. Auto-configuration is split into
per-technology modules, and packages move with it: each module's root package
is `org.springframework.boot.<module>` (for example `@EntityScan` moves to
`org.springframework.boot.persistence.autoconfigure.EntityScan`); "classic"
starters bring all modules for a quick upgrade and should be left later.
**Jackson 3 is the default JSON library**; the deprecated route that keeps
Jackson 2 is on [`jackson`](./jackson.md). Tracing needs a dedicated starter
(`spring-boot-starter-zipkin` or `spring-boot-starter-opentelemetry`).
`spring-boot-starter-aop` is renamed `spring-boot-starter-aspectj`.
`@MockBean` and `@SpyBean` are removed in favour of `@MockitoBean` and
`@MockitoSpyBean`. Undertow support is dropped (no Servlet 6.1). Optional
Maven dependencies are no longer packed into the executable jar
(`<includeOptional>true</includeOptional>` restores that). DevTools live reload
is off by default.

## Upstream docs
- https://spring.io/projects/spring-boot
- https://docs.spring.io/spring-boot/
- https://docs.spring.io/spring-boot/reference/features/external-config.html
- https://docs.spring.io/spring-boot/reference/actuator/endpoints.html
- https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html
- https://github.com/spring-projects/spring-boot/wiki (migration guides per major)
- https://spring.io/support-policy
- https://mvnrepository.com/artifact/org.springframework.boot
