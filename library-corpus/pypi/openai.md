# openai — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`openai` (openai-python) is the official OpenAI Python SDK for calling the
OpenAI API (chat/responses, embeddings, etc.). Being an OpenAI-compatible client,
it can also target other servers implementing the OpenAI API (e.g. self-hosted
inference servers) by setting `base_url`.

## Core API / usage shape
- Instantiate a client: a sync `OpenAI` client and an async `AsyncOpenAI` client
  are both provided. Call the API surface off the client (chat/responses, etc.).
- `base_url`, `api_key`, and `timeout` are set per client instance.
- `extra_body` (and `extra_query` / `extra_headers`) passes non-standard or
  undocumented request parameters not in the standard OpenAI request signature —
  e.g. vendor-specific fields for an OpenAI-compatible backend.

## Idioms & best practices
- Pick the client that matches the calling context; the general async/sync
  boundary rule lives in `../language/python.md`.
- Set `timeout` explicitly per client (short for quick extraction calls, generous
  for long reasoning calls) rather than relying on the default; timed-out requests
  are retried automatically by default.
- Catch `APIStatusError` (and subclasses) rather than a bare `Exception` to
  access request IDs and error detail useful for debugging.

## Upstream docs
- Repo/docs: https://github.com/openai/openai-python
- API reference: https://platform.openai.com/docs/
