# qdrant-client — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`qdrant-client` is the Python SDK for the Qdrant vector database: create
collections, upsert points (vectors + payloads), and run vector search / filtered
queries. The server's own security model (key kinds, network bind, TLS) is a
server concern and lives in `../container/qdrant.md`.

## Install, setup and configuration
- `pip install qdrant-client`; `qdrant-client[fastembed]` adds local embedding
  inference with FastEmbed (ONNX Runtime).
- Constructor defaults, from the source: `port=6333` (REST),
  `grpc_port=6334`, `prefer_grpc=False`, `host` falls back to `localhost`
  when neither `url` nor `host` is given, `timeout` 5 s for REST and gRPC when
  unset, `check_compatibility=True` (the client checks the server version), and
  `https` decided by the API-key rule in the pitfalls below.
- `prefix=` adds a path prefix to every REST URL (for a server behind a
  path-routing proxy); `auth_token_provider=` supplies a bearer token per
  request instead of a static key.

## Core API / usage shape
- The SDK ships both a sync `QdrantClient` and an async `AsyncQdrantClient`.
  `QdrantClient` methods (`query_points`, `get_collection`, `upsert`, `delete`,
  etc.) are blocking.
- The client speaks REST by default. `prefer_grpc=True` switches to gRPC (on
  the server's separate gRPC port), which upstream describes as typically much
  faster for uploading collections.
- Local mode, `QdrantClient(":memory:")` or `QdrantClient(path=...)`, runs the
  same API in-process with no server at all.
- Idempotent bootstrap: `client.collection_exists(name)`, then
  `create_collection(collection_name, vectors_config=VectorParams(size=...,
  distance=Distance.COSINE), sparse_vectors_config={"text": SparseVectorParams()})`.
  Dense and sparse vectors for hybrid search are declared together when the
  collection is created. `recreate_collection` is deprecated in favour of this
  check-then-create form.
- `create_payload_index(collection_name, field_name, field_schema=PayloadSchemaType.KEYWORD)`
  indexes a payload field. Index every field used in a `Filter` or in a delete
  by `FilterSelector`.
- `query_points(..., limit=10, score_threshold=...)` drops results below a
  similarity floor on the server side.
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
- The scheme default depends on the API key: with `api_key` set and no scheme
  in `url=`, the client uses HTTPS (unless `https=False`); without a key it uses
  plain HTTP. A scheme in `url=` overrides the default, so to reach a plain-HTTP
  endpoint with a key pass an explicit `http://` `url=` (the client then warns
  that the key travels over an insecure connection).
- Observed in practice: the vector size is fixed when the collection is
  created, so the collection name, the vector dimension and the embedding model
  are one bundle. Changing one without the others fails silently until the
  first upsert: you write to a collection nothing reads, or read one nothing
  writes. Change all three in one cutover.
- An empty API key fails open. A settings field that defaults to the empty
  string, paired with an environment example that ships the variable blank,
  lets a deployment that forgot the key start and run unauthenticated against a
  server that was also started without one. Assert at startup that the key is
  non-empty wherever authentication is expected.
- The key travels in a request header, so over plain HTTP it crosses the network
  in clear. Use TLS whenever the channel leaves a trusted private network.

## Testing
- Local mode (`QdrantClient(":memory:")`) runs the real API in process; use it
  for contract tests, as the idiom above says. Local mode is not the server, so
  behaviour that depends on server configuration (authentication, TLS) needs a
  real Qdrant.

## Security defaults
- No key means no authentication on the client side; the server decides
  whether that is accepted (`../container/qdrant.md`).
- HTTPS is on by default only when an `api_key` is given without a scheme;
  everything else depends on the URL you pass.
- Observed in practice: a vector store built from personal data is itself a
  personal-data store and carries the erasure obligation. An old collection kept
  for rollback is a second copy. Delete by payload filter is the erasure tool,
  so key every payload by its data subject.

## Operational behaviour
- Every call is a network request (REST, or gRPC with `prefer_grpc=True`) with
  a 5-second default timeout; long bulk operations need a larger `timeout`.
- The gRPC connection pool defaults to 3 connections; the REST pool size is
  inherited from the HTTP library.
- `force_disable_check_same_thread` exists for local mode, and upstream says to
  use it only when you handle thread safety yourself.

## Interop
- LlamaIndex reaches Qdrant through the separate
  `llama-index-vector-stores-qdrant` package (`library-corpus/pypi/llama-index-core.md`).
- The server side (keys, binding, TLS) is on `../container/qdrant.md`.

## Major lines
- This page does not record differences between client major lines. The
  client checks its compatibility with the server version at startup by
  default; keep client and server within the range upstream supports. The
  check accepts the same major with minor versions at most one apart, and a
  mismatch only logs a `UserWarning` (as does a server whose version cannot be
  read); it never refuses the connection. So a server moved past that window,
  to pick up a security fix for example, is a warning to record, not a
  refused connection; a test of the pairing shows whether it works, and set
  `check_compatibility=False` only once the pairing has been tested.

## Upstream docs
- Docs: https://qdrant.tech/documentation/
- Security (API keys, TLS): https://qdrant.tech/documentation/security/
- Repo: https://github.com/qdrant/qdrant-client
