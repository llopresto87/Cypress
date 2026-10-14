# drizzle-orm — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Drizzle is a TypeScript ORM and SQL query builder. A schema is declared in
TypeScript (tables, columns, indexes, enums, relations), the same declaration
types every query, and a separate CLI turns schema changes into SQL migrations.
It is SQL-first: the query builder mirrors SQL, and raw SQL is always one
`sql` template away. It has no engine binary of its own; it wraps a database
driver the project installs beside it. This page covers the PostgreSQL side.
Licence: Apache-2.0 (`drizzle-orm`). Upstream: https://orm.drizzle.team/ (docs,
source at https://github.com/drizzle-team/drizzle-orm-docs) and
https://github.com/drizzle-team/drizzle-orm.

- `drizzle-orm`: the runtime: schema builders, the query builder, relational
  queries, transactions, and one driver adapter and one migrator per supported
  driver. Needed by every project that uses Drizzle.
- `drizzle-kit`: the dev-time CLI that reads the schema and generates, applies,
  pushes or pulls migrations, checks migration history and serves Drizzle
  Studio. Needed only where migrations are authored; the application runtime
  never imports it.

## Install, setup and configuration
- `npm install drizzle-orm <driver>` and `npm install -D drizzle-kit`. The
  driver is a separate package: `pg` for node-postgres (see
  [`pg`](pg.md)), `postgres` for postgres.js, `@electric-sql/pglite` for the
  in-process WASM Postgres (see [`electric-sql-pglite`](electric-sql-pglite.md)).
  `drizzle-orm` declares these as optional peer dependencies.
- **One subpath per driver.** The `drizzle()` factory and the `migrate()`
  function are imported from the driver's own subpath:
  `drizzle-orm/node-postgres` and `drizzle-orm/node-postgres/migrator`,
  `drizzle-orm/postgres-js` and `drizzle-orm/postgres-js/migrator`,
  `drizzle-orm/pglite` and `drizzle-orm/pglite/migrator`. Schema builders come
  from the dialect core, `drizzle-orm/pg-core`; operators and `sql` from
  `drizzle-orm`.
- **Creating the client.** `drizzle(url)` builds the driver's client itself
  (for node-postgres, a `pg.Pool` from the connection string);
  `drizzle({ connection: {...} })` passes driver options through;
  `drizzle({ client })` wraps a client the project already built. The client is
  reachable afterwards as `db.$client`. For PGlite, `drizzle()` with no argument
  is an in-memory database and `drizzle('path')` a persisted one.
- **`drizzle.config.ts`** (`defineConfig` from `drizzle-kit`) configures the
  CLI. The settings:
  - `dialect` (required): `postgresql`, `mysql`, `sqlite`, `turso`,
    `singlestore`; the 1.0 docs add `mssql` and `cockroach`. One config file
    targets one dialect.
  - `schema`: glob path(s) to the schema files. `out`: the migrations folder,
    default `./drizzle`.
  - `dbCredentials`: a `url`, or `host`/`port`/`user`/`password`/`database`/
    `ssl`; for the `pglite` driver, a folder path or `:memory:`.
  - `driver`: only for drivers the dialect cannot infer (`aws-data-api`,
    `pglite`).
  - `migrations`: `{ table, schema }` of the applied-migrations log, default
    `__drizzle_migrations` in schema `drizzle`.
  - `schemaFilter`, `tablesFilter`, `extensionsFilters` (for example
    `["postgis"]`, so extension-owned tables are ignored), `entities.roles`
    (role management, off by default), `introspect.casing` (`camel` default,
    or `preserve`) for `pull`.
  - `breakpoints` (default `true`): writes `--> statement-breakpoint` between
    statements, needed by dialects that cannot run several DDL statements in
    one transaction.
  - `verbose` (default `false`): prints the SQL `push` will run. `strict`
    (0.x only): makes `push` ask for confirmation before it executes; in the
    1.0 line the flag is gone and confirmation of data-loss statements is the
    default (see Major lines).
  - Several config files can live side by side (`--config=drizzle-dev.config.ts`).

## Core API / usage shape
- **Schema.** `pgTable('users', { id: serial('id').primaryKey(), email:
  text('email').notNull(), ... })` with `pgEnum`, column builders (`serial`,
  `integer`, `text`, `boolean`, `timestamp`, `jsonb`, `uuid`, ...),
  `primaryKey`, `uniqueIndex`, `index` and `references`, all from
  `drizzle-orm/pg-core`. Row types come from `typeof users.$inferSelect` and
  `$inferInsert`.
- **Queries.** `db.select().from(t).where(eq(t.id, x))`, `db.insert(t).values(...)
  .returning()`, `db.update(t).set(...).where(...)`, `db.delete(t).where(...)`,
  joins, and `db.execute(sql\`...\`)` for raw SQL; values interpolated into the
  `sql` template become bound parameters.
- **Relational queries.** `db.query.<table>.findMany({ with: {...} })`. On the
  0.x line they need `drizzle(client, { schema })` plus per-table `relations()`
  objects; on the 1.0 line one `defineRelations(schema, r => ...)` object is
  passed as `drizzle(..., { relations })` (see Major lines).
- **Transactions.** `db.transaction(async (tx) => ...)` commits when the
  callback resolves and rolls back when it throws; `tx.rollback()` throws to
  roll back; a nested `tx.transaction` is a savepoint. PostgreSQL options:
  `isolationLevel`, `accessMode`, `deferrable`.
- **Migrations, four ways.** Upstream documents both directions:
  database-first (`drizzle-kit pull` writes a TypeScript schema from a live
  database) and codebase-first, where the TypeScript schema is the source of
  truth and is applied by `drizzle-kit push` (diff straight to the database, no
  files), by `drizzle-kit generate` then `drizzle-kit migrate`, by `generate`
  then `migrate(db, { migrationsFolder })` from the driver's migrator at
  application start, or by `generate` (or `export`) then an external tool.
  `drizzle-kit check` validates the migration history; `drizzle-kit up`
  upgrades old snapshots to the current format; `drizzle-kit studio` serves a
  database browser.

## Idioms & best practices
- **Pick one migration path per environment and keep to it.** `push` is
  upstream's choice for prototyping; generated SQL files reviewed in version
  control are what `migrate` (CLI or runtime) applies. `push` changes the
  database without writing a migration file, so a database that was pushed no
  longer matches what the migration files would build.
- **Read every generated migration before it merges.** `generate` asks
  whether a changed name is a rename or a drop and an add; the answer decides
  whether the data survives.
- **Keep the driver choice in one module.** The factory, the migrator and the
  client type all follow the driver, so a project that runs on two drivers (a
  server Postgres in production, PGlite in tests) selects both the `drizzle()`
  and the `migrate()` import in the same place, from the same switch.
- **Type the database once, against the shared base.** Each driver returns its
  own database class (`NodePgDatabase`, `PgliteDatabase`); in the source both
  extend one PostgreSQL base class (`PgDatabase` on the 0.x line,
  `PgAsyncDatabase` on the 1.0 source branch). Code that must run on either
  driver takes that common shape, not one concrete class; typed against one
  concrete class, callers no longer accept the other driver's client. The
  docs do not discuss multi-driver projects.
- **Close the client in scripts and tests.** `drizzle(url)` on node-postgres
  owns a `pg.Pool`, which keeps a Node process alive until it is ended:
  `await db.$client.end()` in a script or a test teardown.
- **Generated SQL is dialect SQL, not portable SQL.** `drizzle-kit` writes for
  the configured `dialect` only. Two engines can share one migrations folder
  only while the schema stays in the subset both accept (see
  [`electric-sql-pglite`](electric-sql-pglite.md) for the PGlite case).

## General pitfalls
- **The wrong migrator for the client.** Each driver's `migrate()` is typed to
  take that driver's database class, but a project that loads the migrator by
  dynamic `import()` or types its client as a union or a base class gets no
  compile-time check of the pairing. Upstream documents only the per-driver
  paths and says nothing about a mismatched pair; in the source (0.x and the
  1.0 branch) each migrator only hands the database's own dialect and session
  to the shared migration routine, so the pairing is a typing contract. Import
  the factory and the migrator from the same subpath in the same place.
- **0.x runtime migrator and branch merges.** On the 0.x line the migrator
  applies only local migrations whose folder timestamp is later than the last
  applied one (stated in the 1.0 "Changes in v1" page and visible in the 0.x
  source), so a migration generated on a branch before another branch's
  migration was applied is silently skipped. `drizzle-kit check` and a review of
  timestamps after a merge catch it; the 1.0 migrator applies every missing
  migration.
- **One transaction for the batch (0.x source).** The PostgreSQL migrator runs
  all pending migrations in a single transaction, so a statement PostgreSQL
  refuses inside a transaction block, such as `CREATE INDEX CONCURRENTLY`,
  cannot be applied through it.
- **Missing journal (0.x).** The 0.x migrator reads `meta/_journal.json` in the
  migrations folder and throws without it; a copied or partially committed
  migrations folder fails at start, not at build.
- **`push` and data loss.** `push` computes a diff and can drop columns or
  tables. On 0.x set `strict: true` (and `verbose: true`) to see and confirm
  the statements; on 1.0 confirmation is the default, `--force` skips it and
  `--explain` prints the SQL without running it. Never run `--force` against a
  database holding data you need.
- **`schemaFilter` default moved.** On 0.x, `push` and `pull` manage only the
  `public` schema unless `schemaFilter` lists others; on 1.0 they manage every
  schema by default.

## Testing
- Test against a database, not a mock: run the same migrations the deployment
  runs, then the queries. A server container (see
  [`container/postgres`](../container/postgres.md)) or PGlite in-process are
  the two usual choices.
- A fresh database per test file (or a PGlite `clone()` of a migrated
  instance) keeps tests independent without re-running migrations each time.
- If tests run on PGlite while production runs server PostgreSQL, keep one
  gate that runs the migrations and the suite on the production engine;
  passing on one engine is not evidence for the other.
- Close every client in teardown, or the test runner waits on an open pool.

## Security defaults
- Values interpolated through the query builder and the `sql` template are
  sent as bound parameters, and tables and columns placed in the template are
  emitted as escaped names. `sql.raw()` inserts its text with no parameter and
  no escaping: never pass user input to it.
- Drizzle holds no credentials of its own; the driver's connection settings
  (TLS included, through `ssl` in the connection options or `dbCredentials`)
  decide how the connection is secured.
- `drizzle-kit` connects with the credentials in `drizzle.config.ts`: keep them
  in the environment, and give `migrate` a role that may run DDL while the
  application role does not need to.
- `push --force` (1.0) and `push` without `strict` (0.x) can drop data without
  asking.

## Operational behaviour
- Drizzle adds no connection management of its own: pooling, timeouts and
  reconnection are the driver's (`pg.Pool` for node-postgres).
- The runtime migrator creates the migrations schema and table if missing,
  reads the migrations folder from disk at start, and applies what is pending.
  Deployments that run it at application start need the migrations folder in
  the shipped artifact.
- Nothing in Drizzle runs before a query: a schema mismatch shows as a SQL
  error from the database at the first query that touches it.

## Interop
- Drivers: [`pg`](pg.md) (node-postgres) and
  [`electric-sql-pglite`](electric-sql-pglite.md); the server image is
  [`container/postgres`](../container/postgres.md).
- Validation: on the 0.x line `drizzle-zod` and its siblings derive validators
  from tables; on 1.0 the same features move into `drizzle-orm/zod`,
  `drizzle-orm/valibot`, `drizzle-orm/typebox`, `drizzle-orm/arktype`.
- External migration tools (Atlas and similar) take `drizzle-kit export`
  output or the generated SQL files.

## Major lines

### 0.x line
- `drizzle-orm@0.x` with `drizzle-kit@0.x`; upstream installs and upgrades
  the two together.
- Migrations folder: numbered SQL files plus `meta/_journal.json` and
  snapshots; the migrator compares timestamps (pitfall above).
- Relational queries v1: `relations()` per table, `drizzle(..., { schema })`.
- `drizzle({ casing: 'camelCase' })` sets column-name casing globally.
- `push`/`pull` manage `public` only by default; `strict` makes `push`
  confirm.

### 1.0 line
- Drizzle's docs site describes the 1.0 line and installs it with the `rc`
  dist-tag (`drizzle-orm@rc`, `drizzle-kit@rc`); check the registry's
  dist-tags for which line `latest` names before upgrading.
- Upgrade path from upstream: run `drizzle-kit up` to convert the migrations
  folder, then apply the breaking changes. The folder drops `journal.json`;
  each migration is its own folder holding `migration.sql` and a snapshot.
  `drizzle-kit drop` is removed. The migrations table gains `name` and
  `applied_at` columns (`up` backfills `name`; existing rows keep a NULL
  `applied_at`), and migrations are matched by folder
  name, so the migrator applies every missing one.
- Relational queries v1 removed: `defineRelations()` and
  `drizzle(..., { relations })`.
- Casing moves to table-level helpers (`snakeCase.table`, `camelCase.table`
  from `drizzle-orm/pg-core`).
- `.array()` no longer chains (use `.array('[][]')`); `.enableRLS()` is
  deprecated for `pgTable.withRLS()`; `.generatedAlwaysAs()` accepts only
  `sql`; `getTableColumns` is deprecated for `getColumns`.
- `drizzle-kit`: `push` confirms data-loss statements by default (`--strict`
  removed, `--force` and `--explain` added), `push`/`pull` manage all schemas,
  `check` detects non-commutative migrations across branches
  (`--ignore-conflicts` bypasses it), `pull --init` marks the pulled state as
  applied, and config files may use top-level `await`.
- Validator packages fold into `drizzle-orm/*` subpaths.

## Upstream docs
- https://orm.drizzle.team/docs/overview
- https://orm.drizzle.team/docs/get-started-postgresql
- https://orm.drizzle.team/docs/connect-pglite
- https://orm.drizzle.team/docs/migrations
- https://orm.drizzle.team/docs/drizzle-config-file
- https://orm.drizzle.team/docs/kit-overview (and the `drizzle-kit-*` command
  pages: generate, migrate, push, pull, check, up, export, studio)
- https://orm.drizzle.team/docs/transactions
- https://orm.drizzle.team/docs/upgrade-v1 and
  https://orm.drizzle.team/docs/v0-v1-changes
- https://orm.drizzle.team/docs/relations-v1-v2
- Source: https://github.com/drizzle-team/drizzle-orm (driver adapters and
  migrators under `drizzle-orm/src/<driver>/`)
