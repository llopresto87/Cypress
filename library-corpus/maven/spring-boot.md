# spring-boot — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
An opinionated JVM application framework that stands up production-ready Spring
applications with minimal configuration. It provides auto-configuration (beans
are wired based on what is on the classpath), a curated starter-dependency BOM,
an embedded servlet container so an app runs as a self-contained executable jar,
and Actuator for production operations. Canonical coordinates:
`org.springframework.boot:spring-boot-starter-parent` as the parent POM (or the
`spring-boot-dependencies` BOM imported in `dependencyManagement`), plus
`spring-boot-starter-*` modules (e.g. `spring-boot-starter-web`,
`spring-boot-starter-actuator`) for each capability.

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
- Externalized configuration is layered (property/YAML files, environment
  variables, command-line args, profiles) and bound into typed configuration
  objects.

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

## Upstream docs
- https://spring.io/projects/spring-boot
- https://docs.spring.io/spring-boot/
- https://mvnrepository.com/artifact/org.springframework.boot
