# spring-data-mongodb — maven

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Spring's document-persistence layer for MongoDB. Domain objects are mapped to
documents (`MappingMongoConverter`), repositories are interfaces whose
implementations Spring Data generates (`MongoRepository`), and
`MongoTemplate`/`ReactiveMongoTemplate`, GridFS templates, auditing and
transactions sit beside them. The library is
`org.springframework.data:spring-data-mongodb`, versioned by the Spring Data
release-train BOM; applications add
`org.springframework.boot:spring-boot-starter-data-mongodb` (or
`org.springframework.boot:spring-boot-starter-data-mongodb-reactive`). On the
Boot 4 line the test support is
`org.springframework.boot:spring-boot-starter-data-mongodb-test` (or
`org.springframework.boot:spring-boot-starter-data-mongodb-reactive-test`).
The current 5 line needs JDK 17 and Spring Framework 7. Upstream home:
https://spring.io/projects/spring-data-mongodb, reference at
https://docs.spring.io/spring-data/mongodb/reference/ (it publishes a
release-train matrix of module line, minimum driver and tested servers).

## Install, setup and configuration
- Boot's default connection is `mongodb://localhost/test` (port 27017 when no
  port is set). Set `spring.mongodb.uri`, or host, port, database, username and
  password; on Boot 2 and 3 these keys are `spring.data.mongodb.*` (see Major
  lines). A user-defined `MongoClientSettings` bean is used as it is.
- `spring.data.mongodb.auto-index-creation` turns annotation-driven index
  creation on; it is off by default.
- On the 5 line Spring Data sets no default UUID or BigDecimal/BigInteger
  representation. Set `UuidRepresentation` (Boot 4:
  `spring.mongodb.representation.uuid`) and `BigDecimalRepresentation` (Boot 4:
  `spring.data.mongodb.representation.big-decimal`) explicitly;
  `BigDecimalRepresentation.STRING` keeps the earlier behaviour.

## Core API / usage shape
- **Documents:** POJOs annotated `@Document`, with an `@Id` field. The default
  collection name is the simple class name with a lower-case first letter
  (`SavingsAccount` → `savingsAccount`); `@Document(collection = "...")`
  overrides it. Nested objects are stored embedded, not as references.
- **Type hints:** `DefaultMongoTypeMapper` stores the fully qualified class
  name under `_class` for top-level documents and for values whose type is a
  subtype of the declared property type. `@TypeAlias("...")` stores a short key
  instead; an alias resolves only once the mapping context knows the type
  (first save, or the initial entity set).
- **Repositories:** interfaces extending `MongoRepository<T, ID>`, with CRUD and
  derived query methods; `@Query` for JSON queries.
- **`MongoTemplate`:** queries, updates and aggregations the repository
  abstraction does not cover.
- **Indexes:** `@Indexed` and `@CompoundIndex` create indexes only for
  `@Document` types and only when auto-index creation is on. The reference
  recommends creating indexes explicitly (`IndexResolver` plus
  `IndexOperations.ensureIndex`, for example on `ContextRefreshedEvent`),
  because Spring Data cannot recreate indexes for a collection recreated while
  the application runs.
- **Transactions:** built on client sessions, and disabled unless a
  `MongoTransactionManager` (or `ReactiveMongoTransactionManager`) bean exists.
  `MongoTemplate` picks up the bound session.
- **Auditing:** `@EnableMongoAuditing` (`@EnableReactiveMongoAuditing`) with an
  `AuditorAware` bean.
- **GridFS:** `GridFsTemplate`/`ReactiveGridFsTemplate` store, find and delete
  files with metadata. GridFS is for files beyond the 16 MiB BSON document
  limit; the default bucket `fs` uses the `fs.files` and `fs.chunks`
  collections.
- Collections are schemaless: no DDL, no entity-relationship mapping. Related
  data is embedded or referenced by id, not joined.

## Idioms & best practices
- Use `MongoRepository` for CRUD and simple queries; drop to `MongoTemplate`
  for aggregation pipelines and complex updates.
- Declare `@Document(collection = "...")` when the collection name must
  survive a class rename, and `@TypeAlias` on persisted types that may be
  renamed or moved.
- Create indexes explicitly at startup rather than relying on annotations.
- Embed sub-documents that are read together; reference large or shared data
  by id. Choose per access pattern instead of normalizing out of habit:
  relational and JPA habits do not carry over.

## General pitfalls
- **Renames.** Renaming a mapped class without an explicit `collection` writes
  to a new collection, and without `@TypeAlias` the stored documents still carry
  the old `_class`. Observed in practice: the old collection is orphaned and
  old documents fail to read.
- **No schema migration.** The effective document shape is the current class
  plus every historical shape already stored. Renaming a field does not
  rewrite stored documents; handle old shapes or migrate the data explicitly.
- **Indexes silently missing** while auto-index creation is off (the default
  since the 3.0 line).
- **Transactions need a replica set.** A standalone server does not support
  them (the MongoDB manual requires a multi-node replica set or a sharded
  cluster); add `replicaSet` to the URI. Collection operations, including the
  implicit collection creation of a first insert, are not allowed inside a
  transaction.
- **No cross-store transaction.** Observed in practice: a write that touches a
  JPA store and a Mongo store can partly succeed; the reference describes only
  MongoDB transaction managers.
- **No joins or referential integrity.** Cross-document consistency is the
  application's job. Observed in practice: a deleted GridFS file leaves every
  `_id` stored elsewhere dangling, and embedded snapshots (denormalized copies)
  go stale when the source changes.
- **Boot 4 key move.** An old `spring.data.mongodb.uri` or `host` key no longer
  configures the client, which falls back to `mongodb://localhost/test`.
  Observed in practice: the application starts "healthy" against nothing.
  `spring-boot-properties-migrator` reports renamed keys at startup when it is
  on the class path.
- **Representations on the 5 line.** With no UUID or BigDecimal default, data
  written under the old defaults is read with whatever is now configured, so
  set the old representation explicitly when upgrading (an inference from the
  removed defaults).
- Schemaless collections mean a mapping mistake fails at read or write time,
  not at a schema check.

## Testing
- `@DataMongoTest` configures a `MongoTemplate`, scans `@Document` classes and
  configures repositories; it skips regular `@Component` and
  `@ConfigurationProperties` beans.
- Boot 3 removed the embedded (Flapdoodle) MongoDB auto-configuration. Use
  Flapdoodle's own auto-configuration library, or Testcontainers: a
  `MongoDBContainer` (or `MongoDBAtlasLocalContainer`) with
  `@ServiceConnection` defines the connection details on its own.
- Guard mapping across a framework major with a round-trip test against a real
  server that includes documents written by the old mapping (observed in
  practice as the gate that catches the upgrade breaks above).

## Security defaults
- In `@Query` strings, `String` values bound through `?0` are escaped, so an
  argument cannot add operators. SpEL (`?#{...}`) can build operators and
  objects, and the reference says to sanitize strings passed to it. The escape
  guarantee covers `String` parameters only, not `Map` or `Document`
  arguments.
- Boot's default target is an unauthenticated `mongodb://localhost/test`;
  credentials and TLS (`spring.mongodb.ssl.*` on Boot 4) are opt-in.

## Operational behaviour
- When auto-index creation is on, it runs for the initial entity set at
  startup and on the first access of each entity type.
- On the 5 line the change-stream `DefaultMessageListenerContainer` starts
  automatically, and JMX support is gone in favour of Boot Actuator.
- Boot's MongoDB health check (Boot 3 on) runs `isMaster` and reports
  `maxWireVersion`.

## Interop
- **MongoDB Java driver** (sync and reactive), configured by Boot.
- **Testcontainers** for real-server tests.
- **Querydsl** Mongo module: [`querydsl.md`](./querydsl.md).
- **Spring Data JPA** in the same service: separate transaction managers, no
  shared transaction ([`spring-data-jpa.md`](./spring-data-jpa.md)).

## Major lines
### 2.x to 3.x (Boot 2 era)
- Requires the 4 line of the Java driver: the uber `mongo-java-driver` gives
  way to `bson`, `driver-core` and `driver-sync`; `DBObject` is gone (use
  `org.bson.Document`); `com.mongodb.client.MongoClient` and
  `MongoClientSettings` replace the legacy client;
  `AbstractMongoClientConfiguration` replaces `AbstractMongoConfiguration`;
  auto-index creation is off by default.

### 3.x to 4.x (Boot 3)
- Jakarta and Java 17 baseline of the Spring Data 2022.0 train; a newer 4-line
  driver; Boot 3 drops embedded Mongo auto-configuration.

### 4.x to 5.x (Boot 4)
- Requires the 5 line of the Java driver (4-line support removed); no UUID or
  BigDecimal defaults; the listener container auto-starts; JMX is gone. Boot 4
  moves connection keys from `spring.data.mongodb.*` to `spring.mongodb.*`
  (`uri`, `host`, `port`, `database`, `username`, `password`,
  `authentication-database`, `replica-set-name`, `additional-hosts`,
  `protocol`, `ssl.*`, `representation.uuid`) and management keys from `mongo`
  to `mongodb`. Keys that need Spring Data stay under `spring.data.mongodb.*`
  (`auto-index-creation`, `field-naming-strategy`, `gridfs.bucket`,
  `gridfs.database`, `repositories.type`).

## Upstream docs
- https://spring.io/projects/spring-data-mongodb
- https://docs.spring.io/spring-data/mongodb/reference/
- https://docs.spring.io/spring-boot/reference/data/nosql.html
- https://www.mongodb.com/docs/manual/core/transactions/
