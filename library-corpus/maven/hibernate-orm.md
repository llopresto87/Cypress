# hibernate-orm — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
The dominant Java object-relational mapping (ORM) framework and the usual JPA
provider sitting beneath [`spring-data-jpa`](./spring-data-jpa.md), which owns
the repository layer above it. It maps annotated entity classes to relational
tables, manages a persistence context / session, translates object graphs into
SQL, and provides its own query language (HQL/JPQL) and a `Criteria` API.
Canonical coordinates: `org.hibernate.orm:hibernate-core`.

## Core API / usage shape
- **Entity ↔ schema mapping**: `@Entity`, `@Table`, `@Column`, `@Id` with a
  generation strategy, and relationship annotations (`@OneToMany`,
  `@ManyToOne`, `@ManyToMany`, `@OneToOne`) describe how object graphs map to
  rows and foreign keys.
- **Persistence context / session**: the `Session` (JPA `EntityManager`) tracks
  managed entities, provides first-level caching within a transaction, and
  flushes dirty state to the database.
- **Schema generation (`ddl-auto`)**: Hibernate can create/update/validate the
  schema from the mapping metadata (`none` / `validate` / `update` /
  `create` / `create-drop`), driven by a configuration property.
- **Queries**: HQL/JPQL (object-oriented query language over entities), native
  SQL when needed, and the `Criteria` API for programmatic queries. Typed-query
  DSLs (metamodel/criteria-based query builders, e.g.
  [`querydsl`](./querydsl.md)) are built on top of this JPA substrate.

## Idioms & best practices
- Let a versioned migration tool own the real schema in production and set
  `ddl-auto` to `validate` (or `none`) so the running mapping is checked against
  the migrated schema rather than mutating it.
- Be explicit about fetch strategy: default associations to lazy and fetch what
  you need with join fetches / entity graphs, sizing queries to the use case.
- Keep transaction/session boundaries clear so entities stay managed while you
  traverse their associations.

## General pitfalls
- **Lazy loading / N+1**: accessing a lazy association outside an open
  persistence context throws (`LazyInitializationException`); iterating a
  collection of parents and touching each one's lazy children issues one query
  per parent — the classic N+1 explosion. Fetch deliberately with join
  fetches, entity graphs, or batch sizing.
- `ddl-auto=update` never drops or reconciles removed columns and can diverge
  from intended schema over time — convenient for dev, unsafe as a production
  schema authority.
- Overriding `equals`/`hashCode` on entities with generated IDs, or including
  mutable/associated fields, breaks identity within the persistence context and
  in collections.
- Bidirectional relationships require keeping both sides consistent in memory;
  updating only the owning side (or only the inverse) leads to surprising
  persisted state.

## Upstream docs
- https://hibernate.org/orm/
- https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html
- https://mvnrepository.com/artifact/org.hibernate.orm/hibernate-core
