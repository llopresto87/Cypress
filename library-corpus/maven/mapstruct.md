# mapstruct — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
A compile-time Java bean-mapping framework. A mapping is declared as a
`@Mapper` interface (or abstract class), and an annotation processor generates
the implementation at build time (entity to DTO, say). The generated code is
plain method calls: no reflection, no runtime dependency, compile-time type
safety, and build-time reports for incomplete mappings. Artifacts:
`org.mapstruct:mapstruct` (the annotations) and
`org.mapstruct:mapstruct-processor` (the processor). Spring Boot's BOM does not
manage MapStruct, so the project sets the version. Java 8 or later; Apache 2.0.
Upstream home: https://mapstruct.org, source on GitHub `mapstruct/mapstruct`.

## Install, setup and configuration
- Maven: `mapstruct` as a dependency and `mapstruct-processor` in the
  `maven-compiler-plugin` `annotationProcessorPaths`. Gradle: `implementation`
  plus `annotationProcessor` (and `testAnnotationProcessor` for mappers in test
  code).
- Processor options go in as `-Akey=value` (Maven `compilerArgs`). They are
  defaults that `@Mapper`, `@MapperConfig` and `@BeanMapping` attributes
  override.
- `mapstruct.unmappedTargetPolicy` defaults to `WARN`: a target property with
  no source gives a build warning. `ERROR` fails generation, `IGNORE` stays
  quiet. `@BeanMapping` beats `@Mapper`, which beats the option.
- `mapstruct.defaultComponentModel` defaults to `default`, meaning no
  component model: obtain mappers with `Mappers.getMapper(...)`. Other values
  are `spring` (a singleton Spring bean), `cdi`, `jsr330`, `jakarta` and
  `jakarta-cdi`.
- `mapstruct.defaultInjectionStrategy` defaults to field injection;
  constructor and setter injection are the alternatives.
- Update methods: by default a `null` source property sets the target property
  to null. `NullValuePropertyMappingStrategy.SET_TO_DEFAULT` or `IGNORE`
  change that.

## Core API / usage shape
- **`@Mapper`** declares mapping methods between source and target types, with
  `@Mapping(target = ..., source = ...)` rules for fields whose names differ;
  the processor emits `<Name>Impl`.
- **Generated implementations** are ordinary Java, readable and debuggable.
- **With a DI framework** the reference recommends injecting mappers rather
  than calling `Mappers`:
  `@Mapper(componentModel = MappingConstants.ComponentModel.SPRING)`. Mappers
  listed in `uses` are obtained through the same component model.
- **`injectionStrategy = InjectionStrategy.CONSTRUCTOR`** is the reference's
  recommendation for testability. Use `SETTER` for Spring mappers with circular
  dependencies (compilation can fail otherwise) and for abstract classes or
  decorators.

## Idioms & best practices
- Set `unmappedTargetPolicy` to `ERROR` globally (the option or a shared
  `@MapperConfig`), so an unmapped target fails the build instead of shipping
  nulls. (Semantics upstream; the `ERROR` preference is observed in practice.)
- Spring component model with constructor injection.
- One mapper per aggregate as an explicit DTO boundary keeps the transport tier
  decoupled from the domain model instead of leaking entities across tiers
  (seed advice; upstream is silent).

## General pitfalls
- **Lombok needs the binding processor.** From the Lombok release that
  introduced it (late in the 1.18 series; earlier Lombok needs no binding), `org.projectlombok:lombok-mapstruct-binding` must sit beside
  Lombok; without it, in the reference's words, MapStruct "stops working with
  Lombok". The reference lists `annotationProcessorPaths` in the order
  `mapstruct-processor`, `lombok`, `lombok-mapstruct-binding`. Observed in
  practice: without the binding, the generated mapper can silently skip the
  Lombok-generated accessors and produce null or blank output with no compile
  error. Lombok-generated code may also not match a mapping's expectations;
  adjust the mapping or `lombok.config`.
- **No mapper at all on JDK 23 and later** when the processor is only on the
  compile class path: implicit annotation processing is off by default there,
  and the build succeeds silently. Declare it in `annotationProcessorPaths` (or
  `<proc>full</proc>`).
- `@Named` must be `org.mapstruct.Named`, not `javax.inject.Named`.
- "Could not retrieve @Mapper annotation" means an old `mapstruct` or
  `mapstruct-jdk8` jar arrives through another dependency; exclude it.
- A version bump regenerates every `*MapperImpl`. Read the release's breaking
  changes and the new unmapped-property warnings after a bump (observed in
  practice as the review step).

## Testing
- Constructor injection lets a unit test build the generated mapper with stub
  `uses` mappers, which is the reason the reference gives for it.
- With `unmappedTargetPolicy=ERROR`, the build itself checks mapping
  completeness.

## Security defaults
- MapStruct copies every property that matches by name. A DTO-to-entity
  mapper can therefore copy fields a client should not set (id, role, owner)
  unless they are ignored with `@Mapping(target = ..., ignore = true)` or
  `@BeanMapping(ignoreByDefault = true)`. The by-name rule is upstream; the
  mass-assignment framing is an inference from it. Upstream has no security
  guidance of its own.

## Operational behaviour
- All work happens at compile time; at run time a mapper is plain method calls
  with no reflection or extra dependency. There is nothing else to operate.

## Interop
- **Lombok:** the binding processor and order above.
- **Spring, CDI, JSR-330, Jakarta inject:** component models.
- **Other processors** ([`querydsl.md`](./querydsl.md), Lombok) share the
  compile phase, so processor registration and order are load-bearing.
- Java records are supported as sources and targets.

## Major lines
MapStruct calls each 1.x minor release a major release, so its lines are named
that way upstream.

### 1.6
- Presence checks on source parameters need `@SourceParameterCondition`
  (breaking). `@BeanMapping(ignoreByDefault = true)` applies to target
  properties only (breaking). Adds conditional mapping, annotation pass-through
  and javadoc on generated code. Final versions dropped the `.Final` suffix.

### 1.7
- Native `Optional` support, better Kotlin data and sealed class support, Java
  21 sequenced collections, and new warnings for redundant
  `ignoreUnmappedSourceProperties` entries. It was in beta when this page was
  last checked.

## Upstream docs
- https://mapstruct.org/documentation/stable/reference/html/
- https://mapstruct.org/faq/
- https://github.com/mapstruct/mapstruct/releases
