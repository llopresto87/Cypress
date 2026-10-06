# redis — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`redis-py` (PyPI package name `redis`) is the Python client library for Redis.
It provides both a sync client (`redis.Redis` / `redis.from_url`) and an async
client (`redis.asyncio`).

## Install, setup and configuration
- `pip install redis`; `pip install "redis[hiredis]"` adds the compiled
  `hiredis` response parser, which the client uses when it is installed.
- `redis.Redis(host="localhost", port=6379, db=0)` are the example defaults;
  `redis.from_url("redis://...")` takes the same settings as a URL.
- Responses are `bytes` unless `decode_responses=True`.
- `protocol=` chooses the wire protocol (2 for RESP2, 3 for RESP3); see the
  major lines below for which is the default.

## Core API / usage shape
- Sync: `redis.from_url(...)` / `redis.Redis(...)`. Async:
  `redis.asyncio.from_url(...)`. The two are distinct clients.
- `decode_responses=True` makes GET/HGET etc. return `str` instead of `bytes`.
- Redis hashes: `hset(key, mapping=fields)` sets multiple fields; TTL for the
  whole hash is set with a separate `expire(key, ttl)` call (`HSET` does not take
  an expiry).
- The client uses internal connection pooling per instance created via
  `from_url()`.
- `hiredis` is an optional acceleration dependency; it is not required.
- Each `Redis` instance gets its own connection pool; share a
  `redis.ConnectionPool` explicitly when several clients should use one.
- `r.pipeline()` batches commands and wraps them in MULTI/EXEC by default
  (`transaction=False` turns that off). `r.pubsub()` returns a separate
  `PubSub` object, because a subscribed connection cannot run other commands.

## Idioms & best practices
- Pick the client that matches the calling context; the general async/sync
  boundary rule lives in `../language/python.md`.
- A common pattern is to set `decode_responses=True` on the sync client and let
  the async client work with raw bytes/JSON.
- When interpolating external input (e.g. a session ID from a request) into a
  Redis key, validate its format first (e.g. a UUID regex) to prevent Redis key
  injection via malformed input.
- Set `protocol=` explicitly (RESP2 vs RESP3) if the wire protocol version
  matters to your code.

## General pitfalls
- Careful response/connection handling matters: connection reuse under async
  cancellation has historically been a source of response data leaking across
  requests in pipeline operations. Do not share a single connection across
  concurrent async tasks carelessly.

## Testing
- Upstream documents no fake server on the pages read for this page. Tests
  that depend on Redis semantics (expiry, transactions, pub/sub) run against a
  real Redis, for example a disposable container.

## Security defaults
- The client connects without authentication or TLS unless the URL or the
  arguments carry them: the `Redis` constructor defaults are `password=None`,
  `username=None` and `ssl=False`, and in `from_url` the `rediss://` scheme
  (not `redis://`) wraps the socket in TLS. The server's configuration
  decides what is accepted.
- Validate external input before it becomes part of a key (the idiom above).

## Operational behaviour
- Connections are pooled per client instance and created on demand; a client
  created per request defeats the pool.
- A subscribed `PubSub` connection is dedicated to pub/sub until it
  unsubscribes.

## Interop
- agno's `RedisDb` session store takes a `redis` client
  (`library-corpus/pypi/agno.md`).
- `redis-om-python` is the upstream-recommended object-mapping layer.

## Major lines

### Lines before 5.x
- RESP2 only.

### 5.x to 7.x lines
- RESP3 is available with `protocol=3`; RESP2 stays the default on the wire.

### 8.x line
- Clients speak RESP3 on the wire by default while keeping RESP2-compatible
  Python response shapes. `protocol=2` forces RESP2, and
  `legacy_responses=False` opts into protocol-independent response shapes,
  which upstream recommends for new projects.

## Upstream docs
- Docs: https://redis.readthedocs.io/en/latest/
- Repo: https://github.com/redis/redis-py
