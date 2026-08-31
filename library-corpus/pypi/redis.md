# redis — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`redis-py` (PyPI package name `redis`) is the Python client library for Redis.
It provides both a sync client (`redis.Redis` / `redis.from_url`) and an async
client (`redis.asyncio`).

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
  requests in pipeline operations — do not share a single connection across
  concurrent async tasks carelessly.

## Upstream docs
- Docs: https://redis.readthedocs.io/en/latest/
- Repo: https://github.com/redis/redis-py
