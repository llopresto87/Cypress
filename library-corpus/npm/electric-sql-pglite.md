# electric-sql-pglite — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
PGlite is PostgreSQL compiled to WebAssembly and packaged as a TypeScript
client library. It runs inside the JavaScript process (Node.js, Bun, Deno, or a
browser page or worker) with no server, no container and no native
dependency. It is not an emulator or a virtual machine: it is the PostgreSQL
engine, run in PostgreSQL's single-user mode with an input/output path into
JavaScript, because a WASM build cannot fork a process per connection. A
database can be ephemeral in memory or persisted to the file system (Node,
Bun, Deno) or IndexedDB (browser). Licence: Apache-2.0. Maintained by
ElectricSQL; upstream home https://pglite.dev/ and the source at
https://github.com/electric-sql/pglite.

- `@electric-sql/pglite`: the engine and client: the `PGlite` class, the
  in-memory, Node and IndexedDB filesystems, the `live` query plugin
  (`@electric-sql/pglite/live`), the multi-tab worker
  (`@electric-sql/pglite/worker`), the OPFS filesystem
  (`@electric-sql/pglite/opfs-ahp`), template helpers
  (`@electric-sql/pglite/template`) and the bundled contrib extensions
  (`@electric-sql/pglite/contrib/<name>`).

Companion packages are cited, not covered here: `@electric-sql/pglite-socket`
(a TCP server in front of an instance), `@electric-sql/pglite-tools`
(`pg_dump`), and one package per external extension
(`@electric-sql/pglite-pgvector` and others, see Install).

## Install, setup and configuration
- `npm install @electric-sql/pglite`. No build step and no system package; the
  engine ships as WASM inside the package.
- **Creating an instance.** `await PGlite.create(dataDir?, options?)` is the
  preferred form: it waits for initialisation and, with extensions, gives the
  instance their namespaces on its type. `new PGlite(dataDir?, options?)` also
  works; queries issued before it is ready wait for it.
- **`dataDir` decides persistence**, by prefix:
  - none, or `memory://`: in memory, gone when the instance closes (the
    default, on every platform);
  - a path, or `file://`: the Node filesystem (Node, Bun, Deno);
  - `idb://<name>`: IndexedDB in the browser. It loads every file into memory
    at start and flushes changed files after each query;
  - `opfs-ahp://<path>`: the Origin Private File System through an access
    handle pool, only inside a Web Worker. Upstream recommends IndexedDB in the
    browser for now, because Safari's limit on open sync access handles stops
    the OPFS filesystem from working there.
- **Options** (`PGliteOptions`): `fs` (a filesystem object instead of a
  prefix), `relaxedDurability` (return results before the flush to storage
  completes; mainly for IndexedDB), `extensions` (see below), `username` and
  `database` (whose permissions and which database of the cluster),
  `loadDataDir` (start from a tarball made by `dumpDataDir()`),
  `initialMemory` (pre-size WASM memory to avoid pauses while it grows),
  `debug` (PostgreSQL debug level 1-5, to the console), `parsers` and
  `serializers` (per type OID), `startParams`, `initDbStartParams` and
  `postgresqlconf` (server and initdb parameters, as for a native server),
  and `pgliteWasmModule`, `initdbWasmModule`, `fsBundle` for bundlers or edge
  runtimes that must supply the assets themselves.
- **Extensions are loaded at start, then created.** Pass them in
  `options.extensions` (`{ namespace: extension }`), then run
  `CREATE EXTENSION`. The package bundles a listed subset of the PostgreSQL
  contrib modules (among them `pgcrypto`, `uuid_ossp`, `pg_trgm`, `hstore`,
  `citext`, `ltree`, `btree_gin`, `btree_gist`, `pg_stat_statements`), imported
  from `@electric-sql/pglite/contrib/<name>`; contrib modules missing from the
  extensions page's list are not available. Others ship as separate packages,
  among them pgvector, PostGIS, Apache AGE, pgmq, pgtap, pg_ivm, pg_uuidv7,
  pg_hashids and pg_textsearch. An extension that is not built for PGlite
  cannot be loaded at all.

## Core API / usage shape
- `query<T>(sql, params?, options?)`: one statement, extended protocol, with
  `$1`-style parameters; returns `{ rows, fields, affectedRows, ... }`.
  `rowMode: 'array'` returns positional rows. The `T` type is a cast, not a
  run-time check.
- ``sql`...` ``: tagged template; interpolated values become parameters, and
  the `identifier`, `raw`, `sql`, `query` helpers from
  `@electric-sql/pglite/template` build larger statements.
- `exec(sql)`: several statements, simple protocol, no parameters. Upstream's
  suggested use is migrations and batch SQL.
- `transaction(async (tx) => ...)`: commits when the callback resolves, rolls
  back when it rejects; `tx.query`, `tx.sql`, `tx.exec`, `tx.rollback()`.
- `listen(channel, cb)` / `unlisten`, `onNotification`: `LISTEN`/`NOTIFY`
  within the instance.
- `dumpDataDir(compression?)` and the `loadDataDir` option: snapshot and
  restore the whole data directory as a tarball. `clone()`: a copy of the
  instance (upstream names test runs over the same data as the use).
- `close()`: shuts the database down cleanly. `ready`, `closed`, `waitReady`.
- `COPY ... FROM '/dev/blob'` with a `blob` query option, and
  `COPY ... TO '/dev/blob'` returning `result.blob`, for import and export.
- `execProtocol` / `execProtocolRaw`: raw wire-protocol access, used by
  adapters such as the socket server.

## Idioms & best practices
- **One instance per process (or per test).** PGlite has exactly one
  connection. Share the instance; do not try to open a second one on the same
  data directory.
- **In the browser, run it in a worker.** `PGliteWorker` with the `worker()`
  wrapper keeps queries off the main thread, and across tabs it elects one
  leader tab that runs the instance and proxies the others to it; a new leader
  starts its own instance when the old one closes.
- **Through an ORM, pass the instance in.** Drizzle's `drizzle-orm/pglite`
  adapter (see [`drizzle-orm`](drizzle-orm.md)), Kysely and others wrap a
  `PGlite` instance; the ORM then issues its queries through it.
- **Keep the schema to what both engines accept** when PGlite stands in for a
  server PostgreSQL. Extensions, server features and parameters that the PGlite
  build lacks or disables (see pitfalls) belong to the production engine only.
  Some projects generate ids in the application rather than in the database
  to stay in that subset; that is a design choice, not something the PGlite
  docs require.
- **Use `dumpDataDir()` for PGlite-to-PGlite copies only** and `pg_dump`
  (`@electric-sql/pglite-tools`) for anything that must outlive a PGlite
  version or reach a server.

## General pitfalls
- **Single connection, serialized queries.** The source wraps every public
  `query` and `exec` in one mutex shared with `transaction`, so queries run one
  at a time and none runs while a transaction is open. Follows from the source
  (the docs say only that PGlite is single-connection): inside a
  `transaction` callback, a query sent on the instance instead of on `tx`
  waits for the transaction that is waiting for it, and hangs. A driver pool
  over a server would instead run that query outside the transaction; neither
  is what the code meant.
- **Not a drop-in for server behaviour.** It runs single-user mode in one
  process: no concurrent sessions, so row locking, isolation levels under
  contention, `LISTEN`/`NOTIFY` between connections and deadlock behaviour
  cannot be exercised; background workers are disabled (from 0.4.3, per the
  changelog); extensions are limited to the builds listed above. A test that
  passes on PGlite says nothing about these on a server.
- **Minor releases can break the data directory.** Upstream: unlike patch
  releases, minor version upgrades "might introduce breaking changes", and
  the upgrade path for persisted data is `pg_dump` from the old version and
  import into the new, with both versions installed side by side under an npm
  alias. A `dumpDataDir()` tarball "may not be compatible with other Postgres
  versions".
- **The PostgreSQL major follows the PGlite minor** (see Major lines): a
  version bump of the package can move the engine across a PostgreSQL major.
- **`relaxedDurability` trades durability for latency**: a result returns
  before the flush to storage completes, so a write the caller has seen
  succeed is not yet stored at that moment.
- **The multiplexing socket server is not a real server.** `pglite-socket`
  can accept several client connections over one PGlite connection; upstream
  warns that this differs from a normal installation and "not all use cases
  are guaranteed to work".
- **Default database changed in 0.4.0**: `postgres` instead of `template1`.
  Data created by an older version in `template1` is not where a newer one
  looks.

## Testing
- Upstream positions PGlite for unit and CI tests: it starts and tears down
  fast, so each test can have a fresh database. `new PGlite()` (in memory) per
  test or per file, migrated before use, gives isolation without shared state.
- For many tests over the same seeded data, migrate and seed one instance,
  then `clone()` it per test (`clone()` exists from 0.2.17).
- When production runs server PostgreSQL, keep at least one gate that runs the
  same migrations and the suite against the production engine (a container,
  see [`container/postgres`](../container/postgres.md)). Reasoning from the
  differences above, not a measured result: everything that depends on
  concurrency, unavailable extensions or server configuration is invisible to
  a PGlite-only suite.
- `close()` every instance in teardown.

## Security defaults
- It opens no network port: only code in the same process (or, in the
  browser, the same origin's worker) can reach it. `pglite-socket` adds a TCP
  listener, bound to `127.0.0.1` by default; `--host=0.0.0.0` exposes the
  database to other machines, which upstream documents as the way to allow
  remote connections. Keep the default unless the network around it is
  trusted.
- A browser database lives in the origin's IndexedDB or OPFS storage,
  readable by any script running in that origin and by anyone with access to
  the browser profile; it is not encrypted by PGlite.
- `exec()` takes no parameters: never build its SQL from user input; use
  `query` or the `sql` template for values.
- `username` connects as that role, and PostgreSQL permissions apply in its
  context; grants written for a server role can be exercised this way.

## Operational behaviour
- Start-up initialises (or opens) the data directory inside the process; with
  `idb://` the whole database is loaded into memory first, so memory use grows
  with the database size, and `initialMemory` avoids pauses while WASM memory
  grows.
- Queries are serialized (pitfall above); a long query blocks every other
  caller of the same instance.
- `close()` shuts the engine down cleanly; call it before the process or
  page goes away.
- Persistence with IndexedDB is per file: PostgreSQL keeps a file per table
  and index, and changed files are flushed whole after each query (a few
  milliseconds, per upstream), or after the result is returned under
  `relaxedDurability`.

## Interop
- ORMs: [`drizzle-orm`](drizzle-orm.md) through `drizzle-orm/pglite` and its
  migrator `drizzle-orm/pglite/migrator`; `drizzle-kit` reaches a PGlite
  directory with `driver: 'pglite'` and a folder path in `dbCredentials`.
  Upstream's ORM page covers Prisma, Drizzle, Kysely, Knex.js, Orange ORM and
  TypeORM.
- The server driver for the same schema in production is [`pg`](pg.md)
  (node-postgres); the server image is
  [`container/postgres`](../container/postgres.md).
- Existing PostgreSQL clients can reach an instance over TCP through
  `@electric-sql/pglite-socket` (with the limits above).

## Major lines
PGlite is on 0.x, and upstream treats a minor release as the line boundary:
minor upgrades may break, patches do not. The PostgreSQL engine moves with it.
- **0.2 line**: `clone()` added in 0.2.17.
- **0.3 line**: engine upgraded to PostgreSQL 17 (0.3.0).
- **0.4 line**: a simplified build with a separate initdb; the default
  database became `postgres` instead of `template1`; background workers
  disabled (0.4.3); ICU support, `copyToFS()` and the `postgresqlconf` option
  (0.4.6).
- **0.5 line**: engine upgraded to PostgreSQL 18 (0.5.0); the external
  extensions moved to their own npm packages.
- Moving persisted data across any of these boundaries is a `pg_dump` and
  re-import, per the upgrade page.

## Upstream docs
- https://pglite.dev/docs/ (getting started), https://pglite.dev/docs/about
- https://pglite.dev/docs/api
- https://pglite.dev/docs/filesystems
- https://pglite.dev/docs/multi-tab-worker
- https://pglite.dev/docs/upgrade
- https://pglite.dev/docs/pglite-socket
- https://pglite.dev/docs/orm-support
- https://pglite.dev/extensions/
- https://github.com/electric-sql/pglite (README "Limitations"; the package
  CHANGELOG under `packages/pglite/`)
