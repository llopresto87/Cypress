# hibernate-orm — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
The dominant Java object-relational mapping (ORM) framework and the Jakarta
Persistence provider beneath [`spring-data-jpa`](./spring-data-jpa.md), which
owns the repository layer above it. It maps annotated entity classes to
tables, manages the persistence context (`Session`, the JPA `EntityManager`),
translates object graphs into SQL, and provides its own query language
(HQL/JPQL), a `Criteria` API and schema tooling. Coordinates:
`org.hibernate.orm:hibernate-core` from the 6 line on; the 5 line was
published as `org.hibernate:hibernate-core`. Spring Boot's JPA starter brings
it and manages its version. From the 7 line it is licensed under Apache 2.0.
Upstream home: https://hibernate.org/orm/, user guide and migration guides at
https://docs.hibernate.org.

## Install, setup and configuration
- Under Boot, add the JPA starter; set Hibernate properties through
  `spring.jpa.properties.*` (see [`spring-data-jpa.md`](./spring-data-jpa.md)
  for Boot's own `spring.jpa.*` keys and its naming strategy).
- **Schema action** (`hibernate.hbm2ddl.auto`, Boot
  `spring.jpa.hibernate.ddl-auto`): Hibernate's default is `none`. Actions are
  `none`, `create-only`, `drop`, `create` (drop, then create), `create-drop`,
  `validate` and `update` ("update (alter) the database schema"); current lines
  add `populate`, `truncate` and `synchronize`. "create" is ambiguous: the
  legacy Hibernate value drops first, the JPA standard value does not. Boot
  overrides the default with `create-drop` for an embedded database without
  Flyway or Liquibase, and `none` otherwise.
- `hibernate.hbm2ddl.create_namespaces` defaults to false: Hibernate does not
  create a database schema or catalog itself.
- `hibernate.enable_lazy_load_no_trans` defaults to false. The guide calls it
  unsafe and discouraged: it opens a temporary persistence context for each
  lazy access and can break transaction isolation.
- `hibernate.jdbc.batch_size`: zero or a negative value disables JDBC batching.
- Dialect: from the 6 line, dialects detect the database version, so leave
  `spring.jpa.database-platform` unset or name the version-free dialect
  (`MySQLDialect`, `PostgreSQLDialect`, ...).

## Core API / usage shape
- **Entity mapping**: `@Entity`, `@Table`, `@Column`, `@Id` with a generation
  strategy, and the association annotations (`@OneToMany`, `@ManyToOne`,
  `@ManyToMany`, `@OneToOne`).
- **Defaults to know**: `@ManyToOne` and `@OneToOne` are EAGER by JPA default,
  and EAGER cannot be undone per query. A unidirectional `@OneToMany` maps
  through a link (join) table. `@Enumerated` without a type, or no annotation
  at all, maps an enum as `ORDINAL`.
- **Embeddables**: `@Embedded`/`@Embeddable` value objects usually flatten into
  columns of the owning entity's table; aggregate embeddables (SQL struct,
  JSON, XML) exist from the 6 line on.
- **Identifiers**: `GenerationType.AUTO` is provider-defined. Hibernate maps a
  UUID type to a UUID generator and a numeric type to `SequenceStyleGenerator`,
  which uses a sequence where the database has them and a table otherwise. The
  guide says to use sequences where they exist and `IDENTITY` only where they
  do not (its example is MySQL), at the price that `IDENTITY` disables JDBC
  batching of inserts.
- **Persistence context**: the `Session` tracks managed entities, caches them
  for the transaction (repeatable reads at the application level), and flushes
  dirty state to the database.
- **Queries**: HQL/JPQL over entities, native SQL when needed, and the
  `Criteria` API. Typed-query DSLs such as [`querydsl`](./querydsl.md) build on
  the JPA API.

## Idioms & best practices
- Let a versioned migration tool own the production schema and set `ddl-auto`
  to `validate` (or `none`), so the mapping is checked against the migrated
  schema instead of mutating it.
- Mark associations LAZY and fetch what a use case needs before the
  persistence context closes: `JOIN FETCH` for to-one associations and at most
  one collection, secondary queries or `Hibernate.initialize` for more
  collections (fetching several collections in one join gives a Cartesian
  product).
- Use DTO projections for read-only use cases.
- Map enums with `@Enumerated(EnumType.STRING)`. Observed in practice: with
  STRING, reordering constants is safe but renaming one is a data migration;
  with the ORDINAL default, reordering silently changes stored meaning.
- Keep transaction boundaries clear so entities stay managed while code walks
  their associations.

## General pitfalls
- **Lazy loading and N+1.** Touching a lazy association outside an open
  persistence context throws `LazyInitializationException`; iterating parents
  and touching each one's lazy children issues one query per parent. Turning
  on `enable_lazy_load_no_trans` trades the exception for a query per access
  (observed in practice as N+1 in disguise).
- **equals/hashCode.** The only case that must implement them is an
  identifier class (composite id), from the id values. An id-based
  implementation on a generated id breaks `Set` membership, because the value
  changes when the id is assigned; the guide suggests not implementing them,
  or using a natural id or business key. Observed in practice: Lombok `@Data`
  or `@EqualsAndHashCode` on an entity generates exactly the field-based
  version, so keep those annotations on DTOs.
- **Bidirectional associations.** Both sides must stay consistent in memory.
  A `@OneToMany` without `mappedBy` beside a `@ManyToOne` on the other side is
  two independent mappings, a link table and a foreign key; observed in
  practice, rows then end up duplicated or orphaned.
- **`ddl-auto=update` is not a migration tool.** Upstream says only that it
  alters the schema. Observed in practice: it never drops anything, so a
  renamed field becomes a new column beside the old one (which still holds the
  data), a smaller `@Size` leaves existing rows alone, and a removed entity
  leaves its table. When several deployables map the same tables and each runs
  `update`, the schema is whatever the last one to boot produced. With
  Hibernate Validator on the class path, Bean Validation constraints (`@Size`,
  `@NotNull`) also shape the generated DDL (column length, nullability), so two
  copies of one entity that differ only in validation annotations generate
  different schemas. Compare the copies' annotations to check they agree, and
  treat adding a missing constraint to a table that holds rows as a migration.
- **Cascading persist onto a reference the client chose.** With
  `cascade = ALL` (or `PERSIST`) on an association, a parent built from a
  request that carries an existing child's id makes `persist` meet a detached
  instance and fail with "detached entity passed to persist". Resolve the
  reference by id first (`getReference` or a lookup), answer a missing id with
  a client error, and keep cascades off associations that point at shared
  reference data.
- **Schema-qualified tables.** `@Table(schema = "...")` has no effect on MySQL,
  where a schema is the database, but is real on H2 and PostgreSQL, and
  Hibernate will not create the schema. A mapping that works in production can
  fail in tests, and the reverse (observed in practice; see [`h2.md`](./h2.md)).
- **Removed dialects fail startup.** Naming a version-specific dialect class
  that the line no longer ships (`MySQL5InnoDBDialect`, say) fails at startup
  with a missing class (observed in practice). See Major lines for which classes each line has.
- **Sequence names changed on the 6 line.** AUTO now expects a sequence per
  entity hierarchy named `<entity>_seq` instead of one `hibernate_sequence`, so an
  `import.sql` or a hand-managed schema built for the old name must change.

## Testing
- When moving between ORM major lines, assert the identifier strategy and the
  generated DDL against the production engine in a container: generator naming
  and the dialect classes changed at the 6 boundary. (The changes are
  upstream; the test practice is observed in practice.)
- Cover equals/hashCode with the case the guide shows breaking: add a
  transient entity to a `Set`, persist it, and check it is still found.
- For repository-level test slices, see
  [`spring-data-jpa.md`](./spring-data-jpa.md).

## Security defaults
- Updates outside a transaction are refused by default
  (`hibernate.allow_update_outside_transaction` is false).
- Injection: bind parameters in HQL/JPQL and Criteria; concatenated HQL or
  native SQL is the risk. The fetched Hibernate pages say nothing on injection;
  this is general practice. The binding and `LIKE` escaping rules are on
  [`spring-data-jpa.md`](./spring-data-jpa.md).

## Operational behaviour
- The first-level cache lives as long as the `EntityManager` and is cleared
  when it closes. A second-level cache is tied to the `EntityManagerFactory`;
  the guide lists alternatives to weigh before turning one on.
- Dialects detect the database version from the connection on the 6 and 7
  lines, so one dialect class serves every server version.

## Interop
- **Spring Data JPA / Boot:** the `ddl-auto` default, naming strategy and
  group-id management come from Boot; see
  [`spring-data-jpa.md`](./spring-data-jpa.md).
- **Querydsl** builds queries on the JPA API: [`querydsl.md`](./querydsl.md).
- **Databases:** [`h2.md`](./h2.md) for embedded tests and
  [`mysql-connector-j.md`](./mysql-connector-j.md) for MySQL and MariaDB.
- Hibernate Validator is a separate project.

## Major lines
### 5 line (Boot 2)
- `javax.persistence`, `org.hibernate:hibernate-core`. Version-specific
  dialects (`MySQL5Dialect`, `MySQL57Dialect`, `MySQL8Dialect`, the InnoDB and
  MyISAM variants, ...). With the new generator mappings (the default across
  the line, and Boot 2 keeps them unless
  `spring.jpa.hibernate.use-new-id-generator-mappings=false`) AUTO resolves to
  `SequenceStyleGenerator` with one shared `hibernate_sequence`, table-backed
  on MySQL; the legacy mappings map AUTO to `native` (identity on MySQL).

### 6 line (Boot 3)
- Java 11 baseline, `jakarta.persistence.*` instead of `javax.persistence.*`
  (source-incompatible, so the ORM upgrade is coupled to the framework
  upgrade), group id `org.hibernate.orm`. Dialects detect the database version
  and the version-specific ones are deprecated; the InnoDB variants are already
  gone at the start of the line, and late releases keep only `MySQL8Dialect`
  (deprecated) beside `MySQLDialect`. Sequences are per entity hierarchy
  (`<entity>_seq`), and Boot 3 removed the switch back to old id mappings.
  `@Type(type = "yes_no")` style mappings give way to converters.
- Named queries are parsed and checked at start-up
  (`hibernate.query.startup_check`, on by default), and Spring Data builds
  each `@Query` when it creates the repository, so a query the stricter 6
  parser rejects now stops start-up. A plain identifier that names no
  attribute (a keyword argument such as `octets`) is no longer passed through
  to SQL; wrap it in `sql(...)`. A function Hibernate has not registered
  (MySQL `DATE_FORMAT`) is still rendered as written but typed `Object`, and
  so is `function(...)`, so neither satisfies a DTO constructor projection
  that expects a String (observed in practice as "Missing constructor"). The
  portable `format(<temporal> as '<pattern>')`, with a `DateTimeFormatter`-style
  pattern, returns a String and renders the database's own function.
- Observed in practice on a move from the 5 line straight to the 7 line (no
  migration-guide entry found on either line): on a `Set`-typed
  element collection, generated DDL added a unique key over owner and element
  where the 5 line made a plain index. Accept it when every write path goes
  through the Set, and check existing data for duplicates before `update`
  meets a schema it did not build.

### 7 line (Boot 4)
- Java 17 baseline, the Jakarta Persistence 3.2 spec (disruptive around
  Criteria type parameters), Apache 2.0 licence. `Session#save`, `#update`,
  `#saveOrUpdate` and `#delete` are removed in favour of `persist`, `merge`
  and `remove` (and `CascadeType.SAVE_UPDATE`/`DELETE` in favour of
  `PERSIST`/`MERGE`/`REMOVE`). Only `MySQLDialect` remains for MySQL. Boot 4
  replaces `hibernate-jpamodelgen` with `hibernate-processor`.

## Upstream docs
- https://hibernate.org/orm/
- https://docs.jboss.org/hibernate/orm/current/userguide/html_single/Hibernate_User_Guide.html
- https://docs.hibernate.org/orm/7.0/migration-guide/migration-guide.html
- https://mvnrepository.com/artifact/org.hibernate.orm/hibernate-core
