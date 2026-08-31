# qdrant-client — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`qdrant-client` is the Python SDK for the Qdrant vector database: create
collections, upsert points (vectors + payloads), and run vector search / filtered
queries.

## Core API / usage shape
- The SDK ships both a sync `QdrantClient` and an async `AsyncQdrantClient`.
  `QdrantClient` methods (`query_points`, `get_collection`, `upsert`, `delete`,
  etc.) are blocking.
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
  `client.upsert()` idempotent — re-running a seed overwrites the same points
  instead of duplicating them.

## General pitfalls
- Qdrant returns a 400 error when `query_points` targets a collection with no
  vectors. Pre-check `client.get_collection(name).points_count == 0` (or handle
  the error) before querying collections that may legitimately be empty.
- The client may default to HTTPS without an explicit `url=`; to talk to a
  plain-HTTP endpoint pass an explicit `http://` `url=`.

## Upstream docs
- Docs: https://qdrant.tech/documentation/
- Repo: https://github.com/qdrant/qdrant-client
