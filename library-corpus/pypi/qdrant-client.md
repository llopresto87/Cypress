# qdrant-client — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`qdrant-client` is the Python SDK for the Qdrant vector database: create
collections, upsert points (vectors + payloads), and run vector search / filtered
queries. The server's own security model (key kinds, network bind, TLS) is a
server concern and lives in `../container/qdrant.md`.

## Core API / usage shape
- The SDK ships both a sync `QdrantClient` and an async `AsyncQdrantClient`.
  `QdrantClient` methods (`query_points`, `get_collection`, `upsert`, `delete`,
  etc.) are blocking.
- The client speaks REST by default. `prefer_grpc=True` switches to gRPC (on
  the server's separate gRPC port), which upstream describes as typically much
  faster for uploading collections.
- Local mode, `QdrantClient(":memory:")` or `QdrantClient(path=...)`, runs the
  same API in-process with no server at all.
- `api_key=` sends the key the server checks. Leaving it empty or unset sends no
  key, which the client treats as "no authentication".
- Delete by payload filter:
  `client.delete(collection_name=..., points_selector=FilterSelector(
  filter=Filter(must=[FieldCondition(key=..., match=MatchValue(value=...))])))`
  removes points matching an indexed payload field rather than by explicit
  point-ID list.
- The `llama-index-vector-stores-qdrant` `QdrantVectorStore` is a separate
  integration package wrapping a `QdrantClient` instance; it is not part of
  qdrant-client itself.

## Idioms & best practices
- Use `AsyncQdrantClient` from async code; the general async/sync boundary rule
  for the blocking client lives in `../language/python.md`.
- Deterministic point IDs (e.g. `uuid5(NAMESPACE_DNS, source_id)`) make
  `client.upsert()` idempotent: re-running a seed overwrites the same points
  instead of duplicating them.
- Use gRPC for bulk ingestion scripts where upload time matters. It is a
  performance choice, not a correctness one, so measure before switching.
- Test against local mode when the test needs the real API contract. Hand-rolled
  fakes and mocks of the client are fine for unit tests, but a suite made only
  of them never exercises Qdrant's behavior, so a client or server change that
  alters it passes every gate.
- Give each consumer the narrowest key the server offers. A process that only
  queries should hold a read-only key, not the admin key that can also delete.

## General pitfalls
- Qdrant returns a 400 error when `query_points` targets a collection with no
  vectors. Pre-check `client.get_collection(name).points_count == 0` (or handle
  the error) before querying collections that may legitimately be empty.
- The client may default to HTTPS without an explicit `url=`; to talk to a
  plain-HTTP endpoint pass an explicit `http://` `url=`.
- An empty API key fails open. A settings field that defaults to the empty
  string, paired with an environment example that ships the variable blank,
  lets a deployment that forgot the key start and run unauthenticated against a
  server that was also started without one. Assert at startup that the key is
  non-empty wherever authentication is expected.
- The key travels in a request header, so over plain HTTP it crosses the network
  in clear. Use TLS whenever the channel leaves a trusted private network.

## Upstream docs
- Docs: https://qdrant.tech/documentation/
- Security (API keys, TLS): https://qdrant.tech/documentation/security/
- Repo: https://github.com/qdrant/qdrant-client
