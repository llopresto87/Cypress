# querydsl — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Type-safe query construction for JVM persistence. Instead of hand-writing string
JPQL/HQL (or SQL), queries are composed from a build-time-generated metamodel of
`Q`-classes and expressed as typed predicates, so column and type mistakes surface
at compile time rather than at runtime. The metamodel is produced by an APT
annotation processor that scans the domain model during the build. Querydsl
targets JPA most commonly, but the same predicate model spans other backends
(SQL, Mongo, and others).

## Core API / usage shape
- **Generated `Q`-classes**: one `Q`-class per entity, emitted at build time by
  the annotation processor. Each exposes typed paths for the entity's fields.
- **Typed predicates**: queries are built by combining those paths into
  `BooleanExpression`/`Predicate` values, then handed to a query factory or a
  repository — never assembled as strings.
- **Generic repository boundary**: predicates are frequently consumed through a
  shared/base repository abstraction that accepts a `Predicate` (or builds one)
  rather than declaring a hand-written query method per entity. One generic entry
  point serves many entities.

## Idioms & best practices
- Let predicates flow through a single shared repository abstraction, so filter
  logic is composed and reused instead of re-declared per entity.
- Treat `Q`-class generation as a build step: regenerate on every build and never
  hand-edit the generated sources — they are outputs, not code you own.

## General pitfalls
- **Looks unused, is load-bearing.** There may be no hand-written `Q`-class call
  sites anywhere, because the predicates are consumed generically through a base
  repository. Absence of direct references is NOT evidence the dependency is dead
  weight — removing it breaks the generic query layer.
- **Codegen ordering.** The processor must run BEFORE compilation; stale or
  missing generated sources break the build. Because it shares the compile phase
  with other annotation processors, it can conflict with them — registration and
  processor order are load-bearing, not incidental.
- **BOM-governed versions move silently.** When the version is governed by a
  parent dependency-management BOM rather than pinned directly, an unrelated BOM
  bump can shift it underneath you and force `Q`-class regeneration; a build that
  was green can break until the metamodel is rebuilt.

## Upstream docs
- https://querydsl.com/
- https://github.com/querydsl/querydsl
