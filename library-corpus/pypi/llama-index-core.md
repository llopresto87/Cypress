# llama-index-core — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`llama-index-core` is the core RAG orchestration library of the LlamaIndex
ecosystem: indexes, retrievers, node parsers, storage/docstore, and ingestion.
It is complemented by many companion packages (their own independent versions):
`llama-index-embeddings-*`, `llama-index-readers-*`,
`llama-index-vector-stores-*`, `llama-index-storage-kvstore-*`,
`llama-index-instrumentation`, and `llama-index-workflows`.

## Install, setup and configuration
- `pip install llama-index-core`, plus one companion package per integration
  you use (an embedding provider, a vector store, a reader).
- Global defaults live on `llama_index.core.Settings` (`llm`, `embed_model`,
  the node parser, the callback manager). Components take an explicit argument
  that overrides the global.

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
- `index.as_retriever(similarity_top_k=..., vector_store_query_mode="hybrid",
  alpha=...)` runs dense plus sparse retrieval, with `alpha` weighting the two;
  it needs a vector store with sparse support.
- `VectorStoreIndex.from_vector_store(vector_store, embed_model=...)`
  reattaches to an already populated store with no re-ingest. It raises
  `ValueError` when the store does not keep the node text (`stores_text`).
- `SentenceTransformerRerank(model=..., top_n=...)` reranks retrieved nodes
  with a cross-encoder through `postprocess_nodes(nodes, query_str=...)`. It
  needs `torch` and `sentence-transformers` installed.
- `Document.excluded_embed_metadata_keys` and `excluded_llm_metadata_keys`
  keep chosen metadata keys out of the embedding text and out of the LLM
  context; both default to empty, so all metadata goes in.

## Idioms & best practices
- Chunk with a hierarchical parser, embed leaves, keep parents in the docstore,
  and let a merging retriever reassemble context. That is the canonical
  auto-merging pattern.
- Prefer the async retrieval path for concurrency: call the public
  `retriever.aretrieve()`. `_aretrieve` is the hook a custom retriever overrides
  (its default just calls the synchronous `_retrieve`).

## General pitfalls
- Auto-merging retrieval looks up parent nodes in the docstore by ID; if a parent
  referenced by a retrieved leaf is absent (e.g. after a document is deleted or
  re-ingested leaving stale parent references), the lookup can raise instead of
  degrading gracefully. Guard the parent lookup and fall back to leaf nodes.
- Auto-merging needs the parent nodes in a persistent docstore, not only in the
  vector store. A key-value docstore over an external store (a
  `llama-index-storage-kvstore-*` package) provides one; an in-memory docstore
  loses the parents on restart.
- An unset `Settings.llm` or `Settings.embed_model` resolves to OpenAI's
  models through the separate OpenAI integration packages, so a pipeline that
  forgot to set them calls OpenAI (or fails without a key).

## Testing
- `MockLLM` and `MockEmbedding` stand in for real models. With the environment
  variable `IS_TESTING` set, the "default" LLM and embedding model resolve to
  these mocks instead of OpenAI.
- Test retrieval against a real (local) vector store when the result depends on
  the store's filtering or hybrid scoring; mocks exercise only the pipeline.

## Security defaults
- `SentenceTransformerRerank` defaults to `trust_remote_code=True`, which lets
  the model repository run its own code at load time. Pin the model and set it
  to `False` unless you need the remote code.
- Document metadata is embedded and sent to the LLM by default; use the
  excluded-keys lists to keep identifiers or personal data out of both.

## Operational behaviour
- The default device for the sentence-transformer reranker is chosen
  automatically (`infer_torch_device`) unless `device=` is given.
- The core holds indexes and docstores in memory unless a `StorageContext`
  points them at persistent stores.

## Interop
- Vector stores, embeddings, readers and key-value stores come from separately
  versioned `llama-index-*` packages; Qdrant's is
  `llama-index-vector-stores-qdrant` (`library-corpus/pypi/qdrant-client.md`).
- LLM calls go through integration packages such as the OpenAI one
  (`library-corpus/pypi/openai.md`).

## Major lines
- Core and each integration package version independently. This page does not
  record differences between core major lines; check the integration packages'
  supported core range when bumping core.

## Upstream docs
- Docs: https://docs.llamaindex.ai/en/stable/
- Repo: https://github.com/run-llama/llama_index
