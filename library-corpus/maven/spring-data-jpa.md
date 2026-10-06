# spring-data-jpa — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Spring's relational-persistence layer over JPA, with
[`hibernate-orm`](./hibernate-orm.md) as the usual provider beneath it.
Entities are annotated POJOs, and repositories are declared as interfaces whose
implementations Spring Data generates at runtime (backed by
`SimpleJpaRepository`): CRUD, derived query methods, declared queries
(`@Query`, `@NativeQuery`), Specifications, Query by Example and Querydsl
integration. The library is `org.springframework.data:spring-data-jpa`,
versioned through the Spring Data release-train BOM that Spring Boot imports;
applications add it with
`org.springframework.boot:spring-boot-starter-data-jpa`, which also brings
Hibernate. On the Boot 4 line the test support is its own starter,
`org.springframework.boot:spring-boot-starter-data-jpa-test`. Upstream home:
https://spring.io/projects/spring-data-jpa, reference at
https://docs.spring.io/spring-data/jpa/reference/.

## Install, setup and configuration
- Add the Boot starter and let Boot's BOM pick Spring Data and Hibernate.
- `spring.jpa.open-in-view` registers `OpenEntityManagerInViewInterceptor`,
  which binds an `EntityManager` (and the connection it holds) to the thread
  for the whole request. It defaults to `true` in a web application, and Boot
  logs a startup warning while it is left unset.
- `spring.jpa.hibernate.ddl-auto` (`none`, `validate`, `update`, `create`,
  `create-drop`) defaults to `create-drop` only when an embedded database
  (H2, HSQLDB, Derby) is detected and neither Flyway nor Liquibase is present,
  and to `none` otherwise. Hibernate's own name for it is
  `hibernate.hbm2ddl.auto`.
- Naming: Boot sets Hibernate's `CamelCaseToUnderscoresNamingStrategy` as the
  physical naming strategy, so camel case and dots become underscores and
  table names are lower case (`TelephoneNumber` maps to `telephone_number`).
  Override with `spring.jpa.hibernate.naming.physical-strategy` /
  `implicit-strategy` or a strategy bean.
- `spring.jpa.properties.*` passes native Hibernate/JPA properties through with
  the prefix stripped; `spring.jpa.database-platform` sets the dialect
  explicitly (otherwise the provider detects it).
- `spring.data.jpa.repositories.bootstrap-mode`: `default`, `deferred` or
  `lazy` repository initialization.

## Core API / usage shape
- **Entities**: classes annotated `@Entity` with an `@Id` field mapped to a
  table row.
- **Repositories**: interfaces extending `JpaRepository<T, ID>` (or a narrower
  Spring Data repository interface). Spring generates the implementation:
  CRUD operations, derived query methods whose JPQL is inferred from the method
  name, and `@Query` methods for explicit queries.
- **Composition by interface**: `JpaSpecificationExecutor<T>` adds Criteria
  API Specification queries, `QuerydslPredicateExecutor<T>` adds Querydsl
  `Predicate` finders, and `QuerydslBinderCustomizer<Q>` customizes how web
  request parameters bind to predicates. All can sit on one repository
  interface.
- **Transactions**: methods inherited from `CrudRepository` take their
  configuration from `SimpleJpaRepository`: reads run with
  `@Transactional(readOnly = true)`, everything else with plain
  `@Transactional`. Declared query methods (default methods included) get no
  transaction configuration unless the interface or method declares one.
- **`save()`** calls `EntityManager.persist` when the entity is new and `merge`
  otherwise. Default detection: with a version property of non-primitive type,
  the entity is new when that property is `null`; without one, when the id is
  `null`. A primitive version cannot signal "new", since JPA treats version 0
  as the first inserted version.
- **`Persistable<ID>`**: implementing `isNew()` overrides that detection. The
  reference names an application-assigned id with no version attribute as the
  case that needs it, and shows a `@Transient` flag flipped in
  `@PostPersist`/`@PostLoad`.
- **Lazy reference**: `getReferenceById(ID)` returns a reference without
  loading the row; depending on the provider, touching it when the row does not
  exist throws `EntityNotFoundException`. `getOne` and `getById` are its
  deprecated predecessors.
- **Auditing**: `AuditingEntityListener` (per entity through `@EntityListeners`
  or globally in `orm.xml`) fills the audit fields, an `AuditorAware<T>` bean
  supplies the current user, and the feature needs `spring-aspects` on the
  class path.

## Idioms & best practices
- Let repositories be interfaces; use derived query methods for simple lookups
  and `@Query` for anything the method-name DSL cannot express clearly.
- Put `@Transactional(readOnly = true)` on the repository interface and
  override the write methods with `@Transactional`. When a transaction spans
  several repositories, the reference recommends a service-layer facade that
  owns the boundary.
- Set `spring.jpa.open-in-view=false` for API services, so a request does not
  hold a connection while the response is written. (The setting and its effect
  are upstream; the recommendation for API services is observed in practice.)
- Use auditing annotations and `AuditorAware` instead of hand-maintained
  created/modified bookkeeping.
- Implement `Persistable` when the application assigns ids, so Spring Data does
  not misread insert versus update from id nullness.
- Use `@Modifying(clearAutomatically = true)` when entities changed by a bulk
  query are read again in the same persistence context.
- Own the schema with a versioned migration tool rather than letting the mapping
  shape it; [`hibernate-orm.md`](./hibernate-orm.md) owns the schema-authority
  rule and the `ddl-auto` settings that implement it.

## General pitfalls
- **`readOnly` is a hint, not a guard.** It does not stop a manipulating query
  from running (some databases reject writes in a read-only transaction). With
  Hibernate, Spring sets the flush mode to `MANUAL` (the 2.x reference says
  `NEVER`), so dirty checks are skipped.
- **A read-write base interface.** Because declared methods take the
  interface's configuration, a repository base annotated
  `@Transactional(readOnly = false)` (or plain `@Transactional`) makes every
  derived read on it run read-write. The mechanism is upstream; the
  base-interface case is observed in practice.
- **A security write in a transaction that ends in an exception is rolled
  back.** Default `@Transactional` rolls back on any `RuntimeException`, so a
  method that revokes a token chain and then throws the 401 exception undoes
  its own revocation. Exclude that exception with `noRollbackFor`, or commit
  the write in its own transaction. A single-use claim written as
  read-check-update is a race between two concurrent requests: make it one
  conditional `UPDATE ... WHERE used = false` and treat zero updated rows as
  reuse. Test both against a real database; a mock cannot show a race or a
  rolled-back write.
- **Assigned ids and `save()`.** An entity with an assigned id and no
  `@Version` is never new to the default detection, so `save()` merges: a
  SELECT then an INSERT, or an overwrite of an existing row. Adding
  `Persistable` changes insert/update detection for that entity, so verify it
  after the change.
- **`@Modifying` does not clear the `EntityManager`** (clearing would drop
  unflushed changes), so it can hold outdated entities after a bulk update.
- **Native queries use physical names.** `@NativeQuery` and
  `@Query(nativeQuery = true)` must name the tables and columns the naming
  strategy produced (`telephone_number`), whereas JPQL uses entity and field
  names. Observed in practice as a common failure after a mapping change.
- **`ddl-auto` changes with the database.** With an embedded database and no
  migration tool it silently defaults to `create-drop`; on a real database it
  defaults to `none`.
- **`ignoreCase` and indexes.** From the 3.x line on, `ignoreCase` operators
  (derived finders, Querydsl, Query by Example) wrap the column in `lower()`,
  so an index built for `upper()` stops being used.
- Lazy-loading and N+1 patterns reach through the repository abstraction
  unchanged: a derived method returning parents still fires one query per lazy
  child. These are provider-level traps described in
  [`hibernate-orm.md`](./hibernate-orm.md).
- Observed in practice: when Bean Validation constraints sit on DTOs and not on
  the entity, they are bypassed when code persists an entity directly. The
  fetched reference pages say nothing on it.

## Testing
- `@DataJpaTest` scans `@Entity` classes, configures repositories, replaces the
  data source with an embedded database when one is on the class path, sets
  `spring.jpa.show-sql=true`, and skips regular `@Component` and
  `@ConfigurationProperties` beans.
- Each data JPA test runs in a transaction that rolls back at the end;
  `@Transactional(propagation = Propagation.NOT_SUPPORTED)` turns that off.
  `TestEntityManager` and a `JdbcTemplate` can be injected.
- `@AutoConfigureTestDatabase(replace = Replace.NONE)` keeps the configured
  database instead of the embedded replacement.
- A test on an embedded database proves behaviour on that database only. See
  [`h2.md`](./h2.md) for the schema-qualified mapping that boots green while
  tables are missing (observed in practice).

## Security defaults
- Bind parameters (`?1`, `:name`); never concatenate request input into JPQL or
  native SQL. For a `LIKE` value from an untrusted source, use the SpEL
  `escape(...)` function with JPQL's `escape` clause. It escapes only `_` and
  `%`, not any extra wildcard a database supports.
- Querydsl web binding resolves every request parameter that matches an entity
  path by default. Exclude sensitive properties
  (`bindings.excluding(user.password)` in the reference) so a request cannot
  filter on them.

## Operational behaviour
- Open EntityManager in View holds the `EntityManager` and its connection for
  the whole request, so lazy loads can run during view rendering and pool
  connections stay checked out longer.
- `deleteAllInBatch` and `deleteAllByIdInBatch` issue one query and leave the
  first-level cache out of step with the database; the javadoc says to flush
  the `EntityManager` first.
- The fetched reference pages cover only these two runtime behaviours; pool
  sizing and connection behaviour belong to the driver and the provider pages.

## Interop
- **Hibernate ORM** is the provider under the Boot starter; mapping, fetching
  and schema behaviour live on [`hibernate-orm.md`](./hibernate-orm.md).
- **Querydsl** through `QuerydslPredicateExecutor`; the reference notes that
  Querydsl's own maintenance slowed and that Spring Data supports the OpenFeign
  fork (`io.github.openfeign.querydsl`) on a best-effort basis. See
  [`querydsl.md`](./querydsl.md).
- **Embedded and production drivers:** [`h2.md`](./h2.md) and
  [`mysql-connector-j.md`](./mysql-connector-j.md).

## Major lines
### 2.x (Boot 2)
- `javax.persistence` packages. `getById` and then `getReferenceById` arrived
  within the 2.x line and `getOne`/`getById` were deprecated in its favour. The
  reference names the read-only flush mode `NEVER`.

### 3.x (Spring Data 2022.0 train, Boot 3)
- Java 17 baseline, Spring Framework 6, Jakarta EE (`jakarta.*` instead of
  `javax.*`). `ListCrudRepository`, `ListQuerydslPredicateExecutor` and other
  `List`-returning variants appear; sorting repositories no longer extend the
  CRUD repositories; `ignoreCase` uses `lower()`. Boot 3 moved to the Hibernate
  6 line under the `org.hibernate.orm` group id and removed
  `spring.jpa.hibernate.use-new-id-generator-mappings`.

### Boot 4
- Boot is modular: the module is `spring-boot-data-jpa` with a test module
  `spring-boot-data-jpa-test`, so `@DataJpaTest` lives in
  `org.springframework.boot.data.jpa.test.autoconfigure` and `@EntityScan` in
  `org.springframework.boot.persistence.autoconfigure`.
  `spring.dao.exceptiontranslation.enabled` becomes
  `spring.persistence.exceptiontranslation.enabled`, and
  `hibernate-jpamodelgen` is replaced by `hibernate-processor`.

## Upstream docs
- https://spring.io/projects/spring-data-jpa
- https://docs.spring.io/spring-data/jpa/reference/
- https://docs.spring.io/spring-boot/reference/data/sql.html
- https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html
- https://docs.spring.io/spring-boot/reference/testing/spring-boot-applications.html
