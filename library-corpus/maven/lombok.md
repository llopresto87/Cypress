# lombok — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Project Lombok is a javac (and Eclipse compiler) **annotation processor** that
writes boilerplate into class files at compile time: accessors (`@Getter`,
`@Setter`), `@Data`, `@Value`, `@Builder`, the `@NoArgsConstructor` /
`@RequiredArgsConstructor` / `@AllArgsConstructor` family,
`@EqualsAndHashCode`, `@ToString`, and logger fields (`@Slf4j`, `@Log`).
Nothing calls Lombok at run time: it is needed to compile, never to run, test
or deploy. Coordinates: `org.projectlombok:lombok`. Spring Boot's BOM manages
its version (`lombok.version`). Home: https://projectlombok.org (feature pages,
setup guides and the changelog, which records the JDKs each release supports).

## Install, setup and configuration
- **Maven, upstream form:** declare it with `<scope>provided</scope>` and also
  list it under `maven-compiler-plugin` `<annotationProcessorPaths>`. Upstream
  calls the processor path mandatory from JDK 23, and from JDK 9 when the build
  compiles modules (`module-info.java`). See [`maven`](../cli/maven.md) and
  [`java`](../language/java.md).
- **Keeping it out of the executable jar.** Spring Boot's repackaging includes
  `provided` dependencies in the fat jar, and Boot excludes only DevTools and
  Docker Compose support automatically; Lombok then ships in every runtime image
  (observed in practice: about 2 MB of compile-only tooling). Exclude it in the
  Boot Maven plugin's `<excludes>`. On Boot 4 `optional` dependencies are no
  longer packed by default, so an `optional` declaration also keeps it out;
  on Boot 3 they were packed.
- **`lombok.config`.** Project-wide settings live in `lombok.config` files,
  read from the source directory upward; put `config.stopBubbling = true` in
  the root one. `java -jar lombok.jar config -g --verbose` lists every key.
  Useful keys: `lombok.addLombokGeneratedAnnotation = true` (marks generated
  code `@lombok.Generated`, which JaCoCo and other coverage tools skip),
  `lombok.accessors.chain`, `lombok.accessors.fluent`, and
  `lombok.jacksonized.jacksonVersion`.

## Core API / usage shape
- `@Data` bundles `@ToString`, `@EqualsAndHashCode`, `@Getter` on all fields,
  `@Setter` on all non-final fields and `@RequiredArgsConstructor` (no
  constructor is generated when one is written by hand). Its parameters, such as
  `callSuper`, cannot be set through `@Data`; add the specific annotation
  explicitly.
- `@Builder` generates a builder; `@Builder.Default` keeps a field initializer
  as the default; `@Builder(toBuilder = true)` adds `toBuilder()`;
  `@Singular` builds collections one element at a time. `@SuperBuilder` covers
  class hierarchies.
- `@EqualsAndHashCode(callSuper = ...)`: with an explicit superclass Lombok
  warns until you choose; `callSuper = true` on a class that extends only
  `Object` is a compile error. Lombok generates `canEqual` so subclasses that
  add state keep the equals contract.
- `@ToString.Exclude` drops a field; `@ToString(onlyExplicitlyIncluded = true)`
  with `@ToString.Include` lists fields one by one.
- `@Jacksonized` on a `@Builder` or `@SuperBuilder` class configures the builder
  for Jackson deserialization (see Major lines for the Jackson generation key).

## Idioms & best practices
- Keep Lombok on the processor path and off the runtime class path.
- Prefer `@Value` or Java records for immutable data, and explicit
  `@Getter` / `@Setter` / `@EqualsAndHashCode` over `@Data` on classes whose
  identity matters.
- Mark generated code for coverage tools with
  `lombok.addLombokGeneratedAnnotation`.
- Pair a JDK bump with a Lombok check: each release notes the JDKs it supports,
  and a framework bump can move Lombok through the BOM as a side effect
  (observed in practice).

## General pitfalls
- **A Lombok older than the compiling JDK breaks** (observed in practice;
  upstream records JDK support per release). It fails either with "cannot find
  symbol" for accessors that real code names, or with a crash in annotation
  processing. A Lombok newer than the JDK is harmless.
- **The in-process compiler** (observed in practice, one build, not stated
  upstream). On JDK 21 a build crashed under Maven's in-process compiler and
  was fixed with `maven-compiler-plugin` `<fork>true</fork>`. Upstream's
  documented setup is the processor-path declaration above, which JDK 23 and
  later require anyway; try that first.
- **`@Data` on ORM entities** generates `equals`, `hashCode` and `toString`
  over every mapped field, mutable and lazy associations included: identity
  changes across persistence states, and `toString` can trigger lazy loads or
  recurse through bidirectional links. The identity rule is owned by
  [`hibernate-orm`](./hibernate-orm.md); `@Data` implies the form it forbids.
- **MapStruct together with Lombok** needs `lombok-mapstruct-binding` and the
  right processor order; owned by [`mapstruct`](./mapstruct.md).
- **Lombok on the runtime module path** causes split-package errors (upstream
  changelog: "shouldn't be, but happens").
- **`@Data` with an explicit superclass** generates equality over this class's
  fields only unless `callSuper` is set.

## Testing
- Lombok needs no test support of its own. The tests that matter are the ones
  for behaviour it generates: entity equality across persistence states, and
  builder plus `@Jacksonized` round-trips through the real mapper (see
  [`jackson`](./jackson.md)).
- A coverage gate counts generated methods unless
  `lombok.addLombokGeneratedAnnotation` is set.

## Security defaults
- An annotation processor runs inside the build with the build's privileges,
  and a substituted artifact can change emitted bytecode without any source
  diff. Verify checksums or signatures of build dependencies, processors above
  all (plant reasoning; upstream does not discuss it).
- Lombok adds no runtime surface when it stays off the runtime class path.

## Operational behaviour
- None at run time: the generated code is ordinary bytecode. The only runtime
  cost comes from shipping the jar by mistake (see the setup section).
- Compile-time behaviour follows the JDK's processor rules; see
  [`java`](../language/java.md).

## Interop
- [`spring-boot`](./spring-boot.md): BOM-managed version; packaging rules above.
- [`jackson`](./jackson.md): `@Jacksonized` and the Jackson 3 naming change
  for single-lower-case-prefix accessors, which the migration guide says
  "affects mostly Lombok usage".
- [`mapstruct`](./mapstruct.md) and [`hibernate-orm`](./hibernate-orm.md) as
  above.

## Major lines
Lombok has stayed on its 1.x line for years; what changes across releases is
JDK support, so the boundaries that matter are the JDK's and Jackson's:

### JDK 23 and later
The processor-path declaration is mandatory (JDK 23 stops class-path processor
discovery).

### Jackson 3
`@Jacksonized` supports both Jackson generations in recent releases.
`lombok.jacksonized.jacksonVersion` picks which annotations to generate (2, 3,
or both while migrating); until it is set Lombok generates Jackson 2
annotations and warns. Make the choice match the mapper the service actually
uses.

## Upstream docs
- https://projectlombok.org/setup/maven
- https://projectlombok.org/features/ (one page per annotation)
- https://projectlombok.org/features/configuration
- https://projectlombok.org/features/experimental/Jacksonized
- https://projectlombok.org/changelog
- https://docs.spring.io/spring-boot/maven-plugin/packaging.html
