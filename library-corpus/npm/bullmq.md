# bullmq — npm

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions. For exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile. The Redis server it
> runs on has its own page, [`container/redis.md`](../container/redis.md).

## What it is
BullMQ is a Node.js job-queue library. Producers add jobs to a named queue,
workers in any number of processes take them, run a processor function, and
move each job to completed or failed, with retries, delays, priorities,
rate limiting, parent-child flows and cron-like Job Schedulers. Its default
backend is Redis, driven through Lua scripts so each state change is atomic;
upstream aims at exactly-once delivery and guarantees at-least-once in the
worst case. The npm package is `bullmq` (MIT). From the 6 line the queue
backend is pluggable and the package also ships a PostgreSQL backend (see
Major lines).

Upstream home: https://docs.bullmq.io/ (guide, patterns, API reference) and
the source at https://github.com/taskforcesh/bullmq. The same organisation
publishes Python, Elixir, PHP and Rust clients that share the Redis data
layout; this page covers the Node.js package. The Redis client it drives by
default is `ioredis`, which this page cites but does not own.

## Install, setup and configuration
- `npm install bullmq`. On the 6 line `ioredis` is an optional peer
  dependency and a Redis user installs it explicitly (`npm install ioredis`);
  on the 5 line it is a direct dependency and arrives with BullMQ. The other
  optional peers on the 6 line are `redis` (node-redis, from its 5 line, for
  the node-redis adapter), `pg` (for the PostgreSQL backend) and
  `bullmq-otel` (telemetry).
- **Redis server.** BullMQ needs Redis 6.2.0 or newer, or a vendor upstream
  lists as tested-compatible. Two server settings are BullMQ requirements,
  not tuning:
  - `maxmemory-policy noeviction`. Upstream calls it the only setting that
    guarantees correct queue behaviour: an evicting policy deletes job, lock
    and marker keys and the queue breaks in ways that look like bugs
    ("Missing lock for job ...").
  - Persistence. Whether queued jobs survive a server restart is entirely a
    Redis persistence question, which upstream answers by recommending AOF;
    the modes and their trade-offs are on
    [`container/redis.md`](../container/redis.md).
- **`connection`.** Every `Queue`, `Worker`, `QueueEvents` and
  `FlowProducer` takes a `connection` option. From the 5 line it is required
  (upstream's release notes: a `Worker` throws when it is missing). It is either a plain options
  object (`{ host, port }`, `{ url }`, any ioredis option), from which
  BullMQ builds its own ioredis client, or an existing client. With no host
  given, the ioredis defaults apply (localhost, 6379).
- **Connection options that change behaviour** (ioredis names, as BullMQ
  documents them):
  - `maxRetriesPerRequest`: how many times a failed command is retried
    before it throws. A `Worker` needs `null` (retry forever). BullMQ sets
    `null` itself on connections it creates for a worker; a hand-built
    ioredis instance passed to a worker must already carry it. The two
    upstream pages word the consequence differently: the connections guide
    says BullMQ throws when a worker is given a client without `null`, the
    production guide says an override makes BullMQ log a warning. Either
    way, fix it. For a `Queue` used by a request handler, leave the default
    (20) or set it low so a caller gets an error instead of waiting.
  - `enableOfflineQueue`: ioredis buffers commands while disconnected. Set
    it to `false` on a producer `Queue` to fail fast; keep it on workers.
  - `retryStrategy`: for connections BullMQ creates, exponential backoff
    between 1 and 20 seconds, retried forever.
  - `keyPrefix` (ioredis) is incompatible with BullMQ; use BullMQ's own
    `prefix` option to namespace queues.
- **Other clients.** BullMQ ships adapters (`createIORedisClient`,
  `createNodeRedisClient`, `createBunRedisClient`, `createValkeyGlideClient`)
  and an `IRedisClient` interface for others; a raw ioredis instance is
  still accepted and wrapped. With a non-ioredis client, configure that
  client's own reconnect and retry behaviour so workers keep retrying.

## Core API / usage shape
- `new Queue(name, { connection, defaultJobOptions, prefix })` is the
  producer and management handle: `add(name, data, opts)`, `addBulk`,
  `getJob`, the getters, `pause`/`resume`, `drain`, `clean`, `obliterate`,
  `upsertJobScheduler`, `close()`.
- `new Worker(name, processor, { connection, concurrency, autorun, ... })`
  starts consuming immediately unless `autorun: false` (then `worker.run()`).
  The processor is `async (job, token, signal) => result`; its return value
  becomes `job.returnvalue`, a thrown `Error` fails the attempt. `signal` is
  an `AbortSignal` for job cancellation. A processor given as a file path or
  URL runs sandboxed in a child process (or a worker thread with
  `useWorkerThreads: true`).
- **Job options** (per job, or as the queue's `defaultJobOptions`):
  `jobId`, `attempts`, `backoff` (`{ type: 'fixed' | 'exponential', delay,
  jitter }` or a custom strategy declared in the worker's
  `settings.backoffStrategy`), `delay`, `priority` (1 is highest, 0 means
  none), `lifo`, `removeOnComplete`, `removeOnFail`, `deduplication`.
- **Job states.** `wait`, `prioritized` or `delayed` on add (`waiting-children`
  for a flow parent), then `active`, then `completed` or `failed`. "Stalled"
  is an event, not a state.
- **Events.** Local events on the instance (`worker.on('completed' |
  'failed' | 'progress' | 'error', ...)`); queue-wide events from any process
  through `new QueueEvents(name, { connection })`, which needs its own
  blocking connection.
- **Flows.** `FlowProducer.add({ name, queueName, data, children })` creates
  a parent that waits for its children.
- **Job Schedulers** (from 5.16.0): `upsertJobScheduler(id, { every |
  pattern, tz, limit, startDate, endDate }, { name, data, opts })` creates or
  updates a recurring job factory idempotently; `getJobSchedulers`,
  `removeJobScheduler`. A scheduler produces the next job only when the
  previous one starts processing, so a saturated queue gets jobs less often
  than the interval.

## Idioms & best practices
- **Make every job idempotent.** Delivery is at least once (a stalled job
  runs again), and retries rerun the whole processor; keep each job small and
  atomic so a second run leaves the same final state.
- **Choose between `jobId` and deduplication deliberately.**
  - A custom `jobId` is unique per queue: adding a job whose id already
    exists is ignored (the first job and its payload stay, a `duplicated`
    event fires). Upstream warns that this lasts only while the job exists:
    once it is removed, manually or by `removeOnComplete`/`removeOnFail`,
    the same id can be added again and runs again. So a `jobId` derived from
    an idempotency key, combined with `removeOnComplete: true`, guards only
    against concurrent duplicates, not against a later replay.
  - `deduplication: { id }` (simple mode) ignores new jobs with the same id
    until the first job completes or fails; with `ttl` it throttles for that
    window; with `ttl`, `extend: true`, `replace: true` and a `delay` it
    debounces, keeping the latest payload; `keepLastIfActive: true` lets at
    most one job run per id and queues one follow-up with the latest data.
    Ignored or replaced jobs emit `deduplicated`.
  - Derive either key from the payload's identity (a hash of the relevant
    fields), never reuse one key for distinct work: a second job with the
    same `jobId` but a different payload is dropped silently (also observed
    in practice).
- **Custom ids** must not contain `:` and must not be all digits (`"123"`
  throws "Custom Id cannot be integers"); prefix numeric business ids.
- **Separate producer and worker connection behaviour.** Producers fail fast
  (`enableOfflineQueue: false`, a low `maxRetriesPerRequest`, catch and
  return an error to the caller); workers wait forever for Redis to return.
- **Reuse `Queue` instances.** Each instance holds at least one Redis
  connection, so create one per queue name per process and cache it rather
  than constructing a `Queue` per request. Connections are cheap enough that
  upstream only asks for reuse under a provider's connection limit; a shared
  ioredis instance can serve several queues, and workers sharing one still
  open their own blocking duplicate.
- **Bound what you keep.** By default completed and failed jobs are kept
  forever. Set `removeOnComplete`/`removeOnFail` to a count or
  `{ age, count }` (keep few completed, many failed for inspection).
- **Attach an `error` listener** to every `Worker` and `Queue`; without one
  Node's unhandled `error` event can stop the worker.
- **Throw `Error` objects** from processors; anything else breaks failure
  handling. Use `UnrecoverableError` to fail without retrying.
- **Scale with processes, then concurrency.** Several workers across
  processes is the recommended setup; `concurrency` > 1 helps only I/O-bound
  processors. CPU-bound work goes to sandboxed processors.
- **Validate configuration before it reaches BullMQ**: an undefined or empty
  queue name or option from the environment surfaces as an opaque Lua error
  ("Lua redis() command arguments must be strings or integers").

## General pitfalls
- **`removeOnComplete` reopens a `jobId`** (see Idioms): a re-add after
  completion runs the work again.
- **An evicting `maxmemory-policy`** silently deletes BullMQ keys; jobs
  vanish or fail with missing-lock errors.
- **A CPU-bound processor stalls jobs.** The worker renews its job lock from
  the event loop (default lock 30 s); a blocked loop lets the lock expire,
  the job is moved back to wait and runs again elsewhere, and after
  `maxStalledCount` stalls (default 1) it fails with "job stalled more than
  allowable limit".
- **Missing lock errors** ("Missing lock for job N. moveToFinished") also
  come from lost Redis connectivity or a job removed while active.
- **A producer `add()` hangs while Redis is down** with the default offline
  queue; an HTTP handler waits with it. The `Queue` also needs Redis online
  when it is instantiated, even with fail-fast settings.
- **Auto-removal is lazy**: old jobs are removed only when another job
  finishes.
- **Job data is stored in clear text** in the backend; keep secrets out of
  it or encrypt the sensitive part before `add`.
- **Mixed versions during a rollout**: an older worker can break on a job
  that uses a feature only a newer producer knows. Upgrade every instance
  first, then ship code that uses the feature.

## Testing
- Upstream ships no in-memory queue. Tests of real queue behaviour run
  against a real Redis (a disposable container) or, on the 6 line, the
  PostgreSQL backend; the backend factory argument also lets a test inject a
  mock `IQueueBackend`. A common alternative is an application-level port
  with an in-process implementation for unit tests and BullMQ behind it, in
  which case the two must agree on dedup semantics (the `jobId` rules
  above), or the unit tests prove behaviour production lacks.
- Use a unique queue name or `prefix` per test run, reset with
  `queue.obliterate()` (or `drain()` for waiting and delayed jobs), and in
  teardown `await` `close()` on every `Worker`, `QueueEvents` and `Queue`,
  then on any shared client: open connections keep the test process alive.
- Test the failure modes upstream lists before production: Redis
  unavailable at startup, a network drop while jobs are active, and a
  graceful shutdown with active jobs.

## Security defaults
- BullMQ adds no authentication of its own: whoever can reach the Redis
  server can read, alter or delete every queue. Secure the server (network
  isolation, ACL user, TLS) per [`container/redis.md`](../container/redis.md)
  and pass credentials and `tls` through the connection options.
- Job payloads, return values and failure reasons are stored unencrypted
  and kept forever unless removal is configured, so personal data in a job
  is a retention question as well as a confidentiality one.
- Sandboxed processors load the file path they are given; never build it
  from job data.

## Operational behaviour
- **Startup**: a `Worker` starts fetching as soon as it is constructed
  (unless `autorun: false`); fetching blocks on Redis rather than polling.
- **Shutdown**: `await worker.close()` stops taking jobs and waits for active
  ones to finish; it has no timeout of its own. Handle `SIGTERM` and
  `SIGINT`, close workers, then queues, then shared connections. A job still
  running when the process is killed is detected as stalled (about 30 s by
  default) and retried by another worker.
- **Failure**: a thrown error moves the job to failed, or back to delayed or
  wait for the next attempt when `attempts` remain; without `backoff` the
  retry is immediate. Exponential backoff waits `2^(attempts-1) * delay`.
- **Reconnection**: connections BullMQ creates reconnect forever with
  exponential backoff; workers resume without intervention.
- **Resource use**: each `Queue` holds one connection, each `Worker` and
  `QueueEvents` one plus a blocking duplicate; Redis memory grows with
  retained jobs.

## Interop
- Redis server, persistence, ACLs and TLS: [`container/redis.md`](../container/redis.md).
- `ioredis` is the default client; node-redis, Bun's client and Valkey Glide
  work through the adapters above.
- The PostgreSQL backend uses `pg`: see [`pg.md`](pg.md).
- Validate configuration and payload shapes before `add` (for example with
  [`zod.md`](zod.md)), since the job data is untyped JSON at rest.

## Major lines

### 1 line
- Delayed jobs, retries with backoff, rate limiting and stalled-job recovery
  need a `QueueScheduler` instance running somewhere for the queue.

### 2 line and later
- `QueueScheduler` is no longer needed: workers handle delayed and stalled
  jobs themselves. Remove it when upgrading.
- From 3.13.0 sandboxed processors can run in worker threads
  (`useWorkerThreads`).

### 5 line
- The `connection` option is required; a `Worker` throws without it.
- Queue markers moved to a dedicated Redis key (a data-structure change, so
  plan the rollout per the upstream migration guide).
- From 5.16.0 Job Schedulers (`upsertJobScheduler`) replace repeatable jobs,
  which stay available but legacy on this line.

### 6 line
- The queue backend is pluggable (`IQueueBackend`), with Redis as the default
  and a PostgreSQL backend (`createPostgresBackend`, needs `pg` and
  PostgreSQL 13 or newer). The `client`, `redisVersion`, `databaseType` and
  `blockingClient` getters are gone; reach Redis through `getBackend()`.
- `ioredis` becomes an optional peer dependency: install it explicitly.
- Legacy repeatable jobs are removed (`repeat` on `add`/`addBulk`, `Repeat`,
  `getRepeatableJobs`, `removeRepeatable*`), and v6 raises an error when it
  meets legacy repeatable metadata in Redis. Migrate each to a Job Scheduler
  while still on the 5 line, delete the legacy entries, then deploy v6.
  `repeat.utc` becomes `tz: 'UTC'`.
- `debounce`, `debounceId` and the `debounced` event are removed (use
  deduplication); deduplication is not allowed on flow parents.
- `resume()` returns a promise and must be awaited; the `paused` job state
  is gone (jobs in a paused queue count as waiting); `Job#discard()` is
  removed (use `UnrecoverableError`); flow jobs without a `jobId` get UUIDs.
- Minimum Node.js is 14.17.0.

## Upstream docs
- Guide: https://docs.bullmq.io/ (connections, job ids, deduplication,
  auto-removal, retrying failing jobs, workers, concurrency, sandboxed
  processors, graceful shutdown, stalled jobs, going to production,
  troubleshooting, PostgreSQL backend)
- Migrations: https://docs.bullmq.io/guide/migrations/migrate-from-v5-to-v6
  and https://docs.bullmq.io/guide/migrations/migration-to-newer-versions
- Changelog: https://docs.bullmq.io/changelog
- Source: https://github.com/taskforcesh/bullmq
- npm: https://www.npmjs.com/package/bullmq
