# spring-data-mongodb — maven

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Spring's document-persistence layer for MongoDB. Domain objects are mapped to
collections of documents, and repositories are declared as interfaces whose
implementations Spring Data generates, analogous to the JPA module but backed by
a document store rather than a relational database. Canonical coordinates:
`org.springframework.boot:spring-boot-starter-data-mongodb`.

## Core API / usage shape
- **Documents**: POJOs annotated `@Document` mapped to a collection, with an
  `@Id` field mapped to the document's identifier.
- **Repositories**: interfaces extending `MongoRepository<T, ID>` (analogous to
  `JpaRepository` but document-backed), providing CRUD and derived query methods
  inferred from method names.
- **`MongoTemplate`**: a lower-level API for queries, updates, and aggregations
  that the repository abstraction does not cover.
- Collections are schemaless: there is no DDL and no entity-relationship
  mapping. Related data is modeled as embedded sub-documents or as arrays of
  referenced identifiers, not as foreign keys and joins.

## Idioms & best practices
- Use `MongoRepository` for standard CRUD and simple queries; drop to
  `MongoTemplate` for aggregation pipelines and complex updates.
- Model related data by embedding sub-documents when it is read together, or by
  referencing IDs when it is large or shared — choose per access pattern rather
  than normalizing reflexively.
- Do not carry relational/JPA habits over. The document model is fundamentally
  different: prefer denormalization and embedding over join-shaped designs.

## General pitfalls
- There is no schema-migration mechanism analogous to a relational migration
  framework. The effective document shape is the current mapped class PLUS
  whatever historical documents already exist in the collection.
- Renaming or restructuring a field in the class does not rewrite documents
  already stored; the application must defensively handle multiple historical
  document shapes, or perform an explicit data migration.
- Do not assume joins or foreign-key referential integrity exist. Cross-document
  consistency is the application's responsibility, not the database's.
- Because collections are schemaless, a mapping mistake fails at read/write time
  rather than at a schema-validation step; test the round-trip mapping
  explicitly.

## Upstream docs
- https://spring.io/projects/spring-data-mongodb
- https://docs.spring.io/spring-data/mongodb/reference/
- https://mvnrepository.com/artifact/org.springframework.boot/spring-boot-starter-data-mongodb
