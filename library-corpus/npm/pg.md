# pg — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
node-postgres is the PostgreSQL client for Node.js: a pure-JavaScript
implementation of the PostgreSQL wire protocol with connection pooling,
parameterized queries, prepared statements, type parsing, `LISTEN`/`NOTIFY`,
and optional native libpq bindings. Its registry name is `pg`; "node-postgres"
is the project's name, not a package. It is the driver underneath most Node.js
query builders and ORMs that target PostgreSQL. Licence: MIT. Upstream docs:
https://node-postgres.com/ ; source (a monorepo that also holds `pg-pool`,
`pg-cursor`, `pg-query-stream`, `pg-connection-string` and `pg-protocol`):
https://github.com/brianc/node-postgres.

- `pg`: the driver itself, exporting `Client`, `Pool`, `Query`, `types` and
  the lazily loaded `native` namespace.

TypeScript declarations are not shipped in the package; they come from the
DefinitelyTyped package `@types/pg`, which a TypeScript project installs as a
dev dependency and keeps on the same line as `pg`.

## Install, setup and configuration
- `npm install pg`. The package is pure JavaScript: no compiler, no libpq. The
  native bindings are an optional peer, `pg-native`, which does need libpq
  and a build toolchain (`pg_config` on the path).
- **Connection parameters** come from the config object, then from the libpq
  environment variables (`PGUSER`, `PGPASSWORD`, `PGHOST`, `PGPORT`,
  `PGDATABASE`, `PGSSLMODE`), then from defaults: user is the process user,
  host `localhost`, port `5432`, database the user name. A `connectionString`
  (`postgresql://user:password@host:5432/db`) is parsed by
  `pg-connection-string`. `password` may be a function, sync or async, that
  returns the password, for short-lived tokens.
- **Client options worth knowing**, all off by default:
  `connectionTimeoutMillis` (no timeout), `statement_timeout` (server-side,
  per statement), `query_timeout` (client-side, per `query` call),
  `lock_timeout`, `idle_in_transaction_session_timeout`, `application_name`,
  `keepAlive`.
- **Pool options** (`new Pool(config)` also passes every client option on to
  each client it creates):
  - `max`: the most clients the pool holds; default 10.
  - `idleTimeoutMillis`: how long an unused client stays connected before it
    is closed; default 10000 ms, and 0 disables the eviction.
  - `connectionTimeoutMillis`: how long `connect()` waits for a new
    connection; default 0, meaning wait forever.
  - `min`: clients kept through idle eviction (the pool does not open them in
    advance); default 0.
  - `allowExitOnIdle`: let the Node.js event loop exit while every client is
    idle; default false.
  - `maxUses`: check-outs before a client is replaced; default unlimited.
  - `maxLifetimeSeconds`: evict a client after this age, whether or not it
    is idle; 0 (disabled) by default.
  - `onConnect(client)`: an async-capable setup hook run on each new client
    before it is handed out; a rejection destroys the client and fails the
    `connect()` that asked for it.
- **TLS** is off unless configured. `ssl` takes `true` or an object passed to
  Node's `tls.connect` (`ca`, `cert`, `key`, `rejectUnauthorized`, ...). See
  Security defaults for how a connection string's `sslmode` maps onto it.

## Core API / usage shape
- **Pool for an application, Client for a one-off.** `new Pool()` creates
  clients lazily. `pool.query(text, values)` checks out an idle client, runs one
  query and releases it. `pool.connect()` returns a client for several
  statements in a row; the caller must `client.release()` it (pass `true` to
  destroy it instead). `pool.end()` waits for checked-out clients, then closes
  every connection and the pool's timers. A standalone `Client` is connected
  with `await client.connect()` and closed with `client.end()`.
- **Parameterized queries.** `query('SELECT * FROM t WHERE id = $1', [id])`
  sends the text and the values separately and the server substitutes them.
  A config object form, `{ text, values, name, rowMode, types }`, adds a
  prepared statement (`name`, prepared once per connection), array rows
  (`rowMode: 'array'`) and per-query type parsers.
- **Results.** `result.rows` (objects keyed by column name), `result.fields`
  (`name`, `dataTypeID`), `result.command`, and `result.rowCount`, which counts
  the rows the command processed (not the rows returned) and is `null` for
  commands with no row count.
- **Transactions** are plain `BEGIN` / `COMMIT` / `ROLLBACK` statements on one
  checked-out client:
  ```js
  const client = await pool.connect()
  try {
    await client.query('BEGIN')
    // ... statements on this client only
    await client.query('COMMIT')
  } catch (e) {
    await client.query('ROLLBACK')
    throw e
  } finally {
    client.release()
  }
  ```
- **Type conversion, outbound.** `null` and `undefined` become SQL `NULL`; a
  `Date` becomes a UTC timestamp string; a `Buffer` passes through; an array
  becomes a PostgreSQL array literal (recursively); an object with
  `toPostgres()` uses its result, any other object is `JSON.stringify`-ed;
  everything else goes through `toString()`.
- **Type conversion, inbound** (`pg-types`): a type without a registered parser
  arrives as a string. `json`/`jsonb` are parsed, `uuid` is a string, `date`,
  `timestamp` and `timestamptz` become `Date`, and `int8` (`bigint`, so also
  `COUNT(*)`) arrives as a **string** because it can exceed JavaScript's safe
  integer range. `types.setTypeParser(oid, fn)` changes a parser globally;
  the `types` option changes it for one client or query.
- **Events.** `pool.on('error')` and `client.on('error')` deliver errors from
  idle connections (a restarted server, a network partition);
  `client.on('notification')` delivers `LISTEN`/`NOTIFY` messages; pool
  events `connect`, `acquire`, `release` and `remove` trace the lifecycle;
  `pool.totalCount`, `idleCount` and `waitingCount` expose its state.
- **Streaming large results** goes through the companion packages
  `pg-cursor` and `pg-query-stream`, which consume a client's connection
  directly (and so do not work with the native bindings).
- **Imports.** CommonJS `require('pg')` and, from 8.15, ESM named imports
  (`import { Pool } from 'pg'`). Before 8.15 ESM code imports the default
  export and destructures it.

## Idioms & best practices
- **One pool per process and database**, created once and shared; upstream
  says an application usually needs one, and that unbounded pools defeat
  pooling. Route every database call through one module that owns the pool,
  so logging, diagnostics and configuration have one home (upstream's
  suggested project structure).
- **Prefer `pool.query` for single statements**: it cannot leak a client.
  Check out a client only when several statements must share a connection.
- **Always release in `finally`.** A client that is never released is gone
  from the pool; once all are gone every later `connect()` waits, forever with
  the default `connectionTimeoutMillis` of 0. Set a connection timeout so a
  leak becomes an error instead of a hang.
- **Attach an `error` listener to every pool** (and every long-lived
  standalone client). An idle connection that dies emits `error`; with no
  listener Node.js treats it as an uncaught error and can crash the process.
  The pool removes the broken client itself.
- **Size `max` against the server's connection limit across every instance**
  of every service that connects, leaving headroom for administration;
  upstream's guidance is that the default of 10 is usually fine, and that
  behind a pooling proxy a small `max` still helps.
- **Run per-connection setup in `onConnect`** (from 8.20), not in the
  `connect` event, whose listener does not await promises.
- **Prefer `timestamptz`** for stored times: `date` and `timestamp` are
  converted in the Node.js process's local time zone (`TZ`), so two processes
  in different zones read different instants. JavaScript `Date` also drops
  microseconds; keep them with a custom parser if they matter.
- **Decide once how `int8` and `numeric` reach JavaScript**: keep the strings,
  parse to `BigInt`, or register a numeric parser only where values are known
  to stay within the safe integer range.

## General pitfalls
- **A process-wide pool keeps the process alive.** Each connected client holds
  a socket reference, so the event loop stays up until every client has idled
  out (`idleTimeoutMillis`, 10 s by default; never, if set to 0) or
  `pool.end()` is called. Long-lived servers do not notice; a script, a
  migration runner or a test suite that builds a pool appears to hang at the
  end or reports open handles. Call `pool.end()` when done, or set
  `allowExitOnIdle: true` for scripts and tests (upstream suggests it for
  exactly those). Observed in practice with a pool built once per process and
  never closed on the application path.
- **`pool.query` cannot run a transaction.** Each call may land on a different
  client, so `BEGIN` on one and `COMMIT` on another leaves a transaction open
  on a pooled connection. Use one checked-out client.
- **A failed statement inside a transaction aborts it.** The client reports
  status `E` (`client.getTransactionStatus()`, from 8.21) and rejects every
  statement until `ROLLBACK`; releasing it without rolling back hands the next
  borrower a broken session.
- **Identifiers cannot be parameters.** `$1` binds values only; a dynamic
  table or column name built by string concatenation is an injection path.
  Upstream points to `pg-format` for escaping identifiers.
- **`COUNT(*)` and `bigint` columns are strings**, so `rows[0].count === 0` is
  never true and arithmetic concatenates.
- **`rowCount` is not `rows.length`.** An `UPDATE` without `RETURNING`
  processes rows and returns none.
- **Connection-string TLS parameters replace the `ssl` object.** If the string
  carries `sslmode`, `sslcert`, `sslkey` or `sslrootcert`, an `ssl` object
  passed beside it is overwritten, and its options (a CA, say) are lost.
- **Prepared statements are per connection.** A named query is parsed and
  planned once on each client that runs it, so through a pool the saving is
  per connection, not per application; upstream calls the feature a power-user
  optimization most queries do not need.
- **`numeric` arrives as a string too** (no parser is registered for it), as
  does any type without a parser.
- **Queuing queries on one client without awaiting** relies on the client's
  internal query queue, which is deprecated from 8.19; the maintainer's
  deprecation note says it is to be removed in the 9 line. Await each
  query, or opt into pipelining (below) deliberately.
- **JavaScript and native drivers differ at the edges.** Upstream advises using
  the same one in development and production.

## Testing
- Upstream has no testing guide. What follows is built on the documented pool
  behaviour above.
- Give each test file (or the whole run) a pool it owns and end it in the
  teardown hook; a pool built at module load by application code needs an
  exported close, or `allowExitOnIdle`, or the runner waits for it.
- Run integration tests against a real server on the same major as
  production (a container: [`container/postgres.md`](../container/postgres.md)).
  For an in-process engine with no server, see
  [`electric-sql-pglite`](electric-sql-pglite.md), which is not identical to
  server PostgreSQL and is reached through a different driver.
- Assert type conversions the code depends on (`int8` as string, time zones)
  explicitly, so a global `setTypeParser` added later shows up as a test
  change.

## Security defaults
- **Parameterized queries are the injection defence**; values never touch the
  SQL text. String-built SQL and dynamic identifiers bypass it.
- **No TLS unless configured.** `ssl: true` verifies the server certificate
  (from the 8 line); `ssl: { rejectUnauthorized: false }` encrypts without
  verifying, which an active man in the middle defeats.
- **`sslmode` in a connection string does not follow libpq by default.**
  Without `uselibpqcompat=true`, `require`, `prefer`, `verify-ca` and
  `verify-full` all set `ssl: true` (full verification), and `no-verify` turns
  verification off. With `uselibpqcompat=true` the libpq meanings apply, so
  `require` encrypts without verifying unless `sslrootcert` is given. Upstream
  warns that any mode short of `verify-full` has security implications.
- **SCRAM channel binding** (SCRAM-SHA-256-PLUS) is opt-in with
  `enableChannelBinding: true`, from 8.14.
- **Passwords are non-enumerable** on client and pool objects (from the 8
  line), so logging a client object does not print the password; logging query
  parameters still can leak secrets, which upstream warns against.

## Operational behaviour
- **Startup** opens no connection: a pool connects lazily on first use, so a
  wrong host or password surfaces at the first query, not at construction. A
  readiness check therefore runs a real query.
- **Under load**, once `max` clients are checked out, further requests wait in
  a FIFO queue (`waitingCount`), bounded only by `connectionTimeoutMillis`.
- **Failure**: an idle client that loses its connection emits `error` and is
  removed; an in-flight query rejects. The pool does not retry queries.
- **Rotation**: `maxLifetimeSeconds` and `maxUses` retire clients so
  connections spread across replaced or rebalanced servers.
- **Shutdown**: `pool.end()` waits for checked-out clients to come back, then
  closes all connections; a later `connect()` on an ended pool errors.
- **Pipelining** (opt-in, `pipeline: true` on a client or pool, from 8.23)
  sends several queries without waiting for each reply; each query keeps its
  own result or error. It has no effect through `pool.query`, which uses a
  client for one query only.

## Interop
- PostgreSQL server and its container image:
  [`container/postgres.md`](../container/postgres.md).
- Drizzle ORM's `node-postgres` driver wraps a `pg` `Pool` or `Client`:
  [`drizzle-orm`](drizzle-orm.md).
- In-process PostgreSQL for development and tests:
  [`electric-sql-pglite`](electric-sql-pglite.md).
- Pooling proxies (PgBouncer and managed equivalents) sit between the pool and
  the server; upstream notes they behave differently from a real backend in
  places, transactions included.

## Major lines

### 7 line
- The module-level singleton (`pg.connect`, `pg.end`) is gone; applications
  create their own `Pool`.
- `client.query` returns a Promise when no callback is given and `undefined`
  when one is; the returned value is no longer an event emitter (pass a
  `Query` object for row events).

### 8 line
- `ssl: true` verifies certificates (`rejectUnauthorized` defaults to true), so
  a self-signed server certificate fails until a CA is supplied or
  verification is explicitly turned off.
- The default database name follows the configured `user`, not the process
  user.
- Passwords are non-enumerable, `pg.native` is non-enumerable, `Pool` is an
  ES6 class, and notices are no longer `Error` instances.
- Additions within the line, per the changelog: `allowExitOnIdle` stops
  blocking the event loop when all clients are idle (8.8), channel binding
  (8.14), ESM named imports (8.15), the pool's `min` (8.16), `connect()`
  resolving to the client (8.18), the internal query queue deprecated (8.19, its removal
  announced for the 9 line),
  `onConnect` (8.20), `getTransactionStatus()` (8.21), direct TLS negotiation
  for PostgreSQL 17 and later with `sslnegotiation: 'direct'` (8.22), query
  pipelining (8.23).

## Upstream docs
- https://node-postgres.com/ (APIs: pool, client, result, types; features:
  connecting, queries, pooling, transactions, data types, SSL, native, ESM,
  pipelining; guides: project structure, pool sizing, upgrading)
- https://github.com/brianc/node-postgres (CHANGELOG.md; docs sources under
  `docs/pages`)
- https://github.com/brianc/node-postgres/tree/master/packages/pg-connection-string
- https://github.com/brianc/node-pg-types
- https://www.npmjs.com/package/pg ; https://www.npmjs.com/package/@types/pg
