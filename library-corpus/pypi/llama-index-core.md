# llama-index-core — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`llama-index-core` is the core RAG orchestration library of the LlamaIndex
ecosystem: indexes, retrievers, node parsers, storage/docstore, and ingestion.
It is complemented by many companion packages (their own independent versions):
`llama-index-embeddings-*`, `llama-index-readers-*`,
`llama-index-vector-stores-*`, `llama-index-storage-kvstore-*`,
`llama-index-instrumentation`, and `llama-index-workflows`.

## Core API / usage shape
- Indexes (e.g. `VectorStoreIndex`) build over parsed nodes; retrievers pull
  relevant nodes at query time.
- `HierarchicalNodeParser.from_defaults(node_parser_ids=..., node_parser_map=...)`
  builds multi-level parent/child chunk hierarchies; pair with `get_leaf_nodes(...)`
  to isolate the embeddable leaf tier while retaining parents in the docstore for
  later merge lookups.
- `AutoMergingRetriever` merges retrieved leaf nodes back up to their parent
  nodes via the docstore.
- `StorageContext` wires together the docstore, index store, and vector store.

## Idioms & best practices
- Chunk with a hierarchical parser, embed leaves, keep parents in the docstore,
  and let a merging retriever reassemble context — the canonical auto-merging
  pattern.
- Prefer the async retrieval paths (`_aretrieve`) for concurrency.

## General pitfalls
- Auto-merging retrieval looks up parent nodes in the docstore by ID; if a parent
  referenced by a retrieved leaf is absent (e.g. after a document is deleted or
  re-ingested leaving stale parent references), the lookup can raise instead of
  degrading gracefully. Guard the parent lookup and fall back to leaf nodes.

## Upstream docs
- Docs: https://docs.llamaindex.ai/en/stable/
- Repo: https://github.com/run-llama/llama_index
