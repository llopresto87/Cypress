# querydsl — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Type-safe query construction for JVM persistence. Instead of hand-written
string JPQL/HQL (or SQL), queries are composed from a build-time-generated
metamodel of `Q`-classes and expressed as typed predicates, so column and type
mistakes surface at compile time. One fluent model spans several backends:
JPA most commonly, also SQL, MongoDB and collections. For JPA it is an
alternative to both JPQL strings and the Criteria API.

There are two upstream homes:
- The original project, `com.querydsl:querydsl-jpa` (runtime) and
  `com.querydsl:querydsl-apt` (annotation processor), home
  https://querydsl.com and GitHub `querydsl/querydsl`. Its last line is 5, and
  it gets no regular releases.
- The OpenFeign fork, `io.github.openfeign.querydsl:querydsl-jpa` and
  `io.github.openfeign.querydsl:querydsl-apt`, home
  https://openfeign.github.io/querydsl and GitHub `OpenFeign/querydsl`. It
  releases regularly on its 6 and 7 lines, keeps the `com.querydsl.*` packages
  and the artifact ids, and calls the original inactive.

The Spring Data reference says Querydsl maintenance slowed and that Spring Data
supports the fork on a best-effort basis. Spring Boot's dependency management
still manages the original `com.querydsl` artifacts through the
`querydsl.version` property and imports `com.querydsl:querydsl-bom`.

## Install, setup and configuration
- **Original 5 line, Maven:** `querydsl-apt` with scope `provided` plus
  `querydsl-jpa`, and `com.mysema.maven:apt-maven-plugin` with goal `process`,
  `outputDirectory` `target/generated-sources/java`, and processor
  `com.querydsl.apt.jpa.JPAAnnotationProcessor`
  (`com.querydsl.apt.hibernate.HibernateAnnotationProcessor` when the domain
  uses Hibernate annotations). The processor finds `@Entity` types and writes a
  query type beside each (`QCustomer` for `Customer`, with a static default
  instance `QCustomer.customer`).
- **Jakarta on the 5 line:** the default (unclassified) artifacts target
  `javax.*`. A Jakarta stack (Boot 3 and later) needs the `jakarta` classifier
  on both `querydsl-jpa` and `querydsl-apt`.
- **Fork 6 line and later:** Jakarta only, Java 17, Hibernate 6+ or
  EclipseLink 4+, Boot 3+. Declare `querydsl-apt` in the
  `maven-compiler-plugin` `annotationProcessorPaths` with a classifier naming
  the processor (`jpa`, `hibernate`, `general`); the fork no longer recommends
  `apt-maven-plugin`. Migrating from the original is a group-id replace.
- **Version overrides under Boot:** with `spring-boot-starter-parent`, override
  the managed version by setting `querydsl.version` in the project's pom. When
  Boot's BOM is imported rather than inherited, a property override does not
  work, and the override goes into `dependencyManagement` ahead of the Boot
  import.

## Core API / usage shape
- **Generated `Q`-classes:** one per entity, exposing typed paths for its
  fields.
- **Query factory:** `JPAQueryFactory` is the preferred way to obtain
  `JPAQuery` instances (`HibernateQueryFactory` for the Hibernate API); both
  implement `JPQLQuery`. Shape:
  `queryFactory.selectFrom(customer).where(customer.firstName.eq("Bob")).fetchOne()`,
  with `innerJoin`/`leftJoin`, `groupBy`, `having` and `orderBy`.
- **DML:** `queryFactory.delete(customer).where(...).execute()` and the update
  clause return the affected row count.
- **Typed predicates:** paths combine into `BooleanExpression`/`Predicate`
  values that a query factory or a repository consumes, never strings.
- **Spring Data:** `QuerydslPredicateExecutor<T>` on a repository adds
  `findAll(Predicate)`, `count`, `exists` and so on
  (`ListQuerydslPredicateExecutor` returns `List` from the Spring Data 3 line);
  `@QuerydslPredicate` resolves a `Predicate` from web request parameters.
  Predicates are often consumed through a shared base repository, so one
  generic entry point serves many entities.

## Idioms & best practices
- Keep the processor and the runtime on the same version, driven by one BOM
  property. (Boot's BOM drives both from `querydsl.version`; observed in
  practice, a mismatch breaks generation.)
- Treat `Q`-classes as build output under `target/generated-sources/java`:
  regenerate on every build and never hand-edit them.
- Let predicates flow through one shared repository abstraction, so filter
  logic is composed and reused instead of re-declared per entity.
- Customize web binding with `QuerydslBinderCustomizer` on the repository (for
  example every String path to `containsIgnoreCase`); a
  `QuerydslBinderCustomizerDefaults` bean sets defaults for all repositories.

## General pitfalls
- **No Q-classes on JDK 23 and later.** Implicit annotation processing (javac
  discovering processors on the compile class path) was deprecated in JDK 21
  and is off by default from JDK 23. The build still succeeds but generates no
  query types. Declare the processor in `annotationProcessorPaths` or set
  `<proc>full</proc>`.
- **javax artifacts on a Jakarta stack.** The unclassified 5-line processor
  looks for `javax.persistence.Entity`, so `jakarta.persistence` entities get
  no Q-classes.
- **DML bypasses JPA.** Update and delete clauses ignore JPA cascade rules and
  do not interact finely with the second-level cache.
- **JSR-305 left the dependency tree on the 5 line.** Code that used
  `javax.annotation.Nullable` through Querydsl's transitive JSR-305 stops
  compiling until JSR-305 is declared directly.
- **Looks unused, is load-bearing.** There may be no hand-written `Q`-class
  call site anywhere, because predicates are consumed through a base
  repository. No direct reference is not evidence the dependency is dead;
  removing it breaks the generic query layer.
- **Binding semantics hide in the base repository.** A
  `QuerydslBinderCustomizer` decides how every list endpoint turns parameters
  into predicates (`eq`, `contains` or `in` by default), so a change there
  changes all of them at once (observed in practice).
- **Version overrides.** `${querydsl.version}` used by a plugin is defined only
  while the Boot parent stays in place. Observed in practice: overriding it on
  the command line (`-Dquerydsl.version=...`) broke the import of the matching
  Querydsl BOM. Upstream documents only pom-property and
  `dependencyManagement` overrides.
- **BOM-governed versions move silently.** An unrelated Boot bump can shift the
  Querydsl version; observed in practice, the metamodel then needs
  regenerating.

## Testing
- Upstream has no testing guide. Observed in practice: a repository test that
  runs a predicate through `@DataJpaTest` (or against the production engine)
  proves the generated Q-classes and the binding together, and a CI check that
  the generated sources exist catches the silent no-codegen case above.

## Security defaults
- Predicates are built from typed paths, so a query is not assembled from
  strings. Spring Data web binding, though, resolves any request parameter that
  matches an entity path unless it is excluded: exclude sensitive properties
  (`bindings.excluding(user.password)` in the reference).

## Operational behaviour
- Querydsl has no runtime component of its own beyond query building. The
  operational fact that matters is maintenance status: the original line gets
  no regular releases, and the fork does.

## Interop
- **Spring Data JPA:** `QuerydslPredicateExecutor` and web binding; see
  [`spring-data-jpa.md`](./spring-data-jpa.md).
- **Spring Data MongoDB:** the Querydsl Mongo module; see
  [`spring-data-mongodb.md`](./spring-data-mongodb.md).
- **Hibernate:** `HibernateAnnotationProcessor` and `HibernateQuery`; see
  [`hibernate-orm.md`](./hibernate-orm.md).
- **Other annotation processors** ([`mapstruct.md`](./mapstruct.md), Lombok)
  share the compile phase, so processor registration is load-bearing
  (observed in practice: their order can matter too).

## Major lines
### 4 line
- `javax` only, with JSR-305 and Guava arriving transitively.

### 5 line (original; Boot 2, and Boot 3+ with the `jakarta` classifier)
- Java 8 minimum. JSR-305 replaced by JetBrains annotations (class retention,
  not transitive); Guava and Joda-Time no longer required. `jakarta`
  classifiers. MDC keys renamed to `querydsl_query` and `querydsl_parameters`.
  Set up with `apt-maven-plugin`.

### Fork 6 and 7 lines (`io.github.openfeign.querydsl`)
- Jakarta only, Java 17. Processor through `annotationProcessorPaths` with
  classifiers. The JDO and Lucene/Hibernate Search modules are removed; R2DBC
  and Kotlin modules are added.

## Upstream docs
- https://querydsl.com/static/querydsl/latest/reference/html/
- https://github.com/querydsl/querydsl
- https://github.com/OpenFeign/querydsl
- https://docs.spring.io/spring-data/jpa/reference/repositories/core-extensions.html
