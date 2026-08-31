# fastapi — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`fastapi` is an ASGI web framework for building HTTP APIs with Python type hints,
Pydantic models for request/response validation, dependency injection, and
automatic OpenAPI docs.

## Core API / usage shape
- Construct an app with `app = FastAPI(...)` and define endpoints with
  path-operation decorators (`@app.get`, `@app.post`, ...).
- `FastAPI(lifespan=...)` accepts an async context manager whose `yield`
  separates startup from shutdown.
- `app.state` (and `request.state`) shares clients/pools set up at startup across
  request handlers.
- `APIRouter` modules mounted via `app.include_router(router, prefix=...)`
  organize routes by feature under a shared prefix.
- `StreamingResponse(generator, media_type="text/event-stream")` emits
  Server-Sent Events.

## Idioms & best practices
- Open and close pooled resources (DB pools, caches) in `lifespan` rather than
  in per-event startup/shutdown handlers, storing them on `app.state`.
- For SSE behind a buffering proxy, send `Cache-Control: no-cache` and
  `X-Accel-Buffering: no` headers to disable proxy buffering of the stream.

## Upstream docs
- Docs: https://fastapi.tiangolo.com
- Repo: https://github.com/fastapi/fastapi
