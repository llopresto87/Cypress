# docling-serve — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`docling-serve` is the remote-HTTP **service** sibling of the in-process
`docling` document-conversion package (see the `docling` page). It wraps
Docling's parsing/conversion capability behind a web API so documents are
converted by a running server over the network, rather than by importing the
library into the calling process. From a client's perspective it is a network
service to call, not a Python library whose functions you invoke in-process.

## Core API / usage shape
- **Remote conversion lifecycle**: the typical interaction is asynchronous —
  submit a document (or a source reference) as a conversion request, receive a
  task/job handle, poll the task's status until it completes (or fails), then
  fetch the converted result.
- **HTTP surface**: endpoints exist to submit a conversion, query task status,
  and retrieve the produced output (e.g. structured document / Markdown /
  JSON), plus health/readiness endpoints for the service.
- **Client shape**: callers use an HTTP client (any language) against the
  service's base URL; the heavy parsing dependencies and models live on the
  server side, keeping the client thin.

## Idioms & best practices
- Treat conversion as async: submit, then poll status with backoff, then fetch —
  do not assume a single synchronous request returns the final document,
  especially for large inputs.
- Keep the client decoupled from server internals: depend on the documented
  HTTP contract, not on `docling` library types.
- Because conversion is a network round-trip, apply timeouts, retries on the
  submit/poll calls, and handle the failed-task terminal state distinctly from
  transport errors.

## General pitfalls
- Confusing it with the in-process `docling` package: importing behaviors,
  types, or synchronous call patterns from the library do not apply — this is a
  service boundary with its own latency, availability, and versioning
  independent of the caller.
- Polling too aggressively or without an upper bound wastes resources and can
  overload the service; large documents take real time to convert.
- The server's model/dependency footprint is heavy; a client should not assume
  instant startup or unlimited concurrency on the service.

## Upstream docs
- Docs: https://docling-project.github.io/docling/
- Repo: https://github.com/docling-project/docling-serve
