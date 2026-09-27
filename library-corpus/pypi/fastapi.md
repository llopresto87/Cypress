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
- A path operation declared with plain `def` runs in an external threadpool
  that the framework awaits. One declared `async def` runs directly on the
  event loop, and nothing offloads it.
- `FastAPI(lifespan=...)` accepts an async context manager whose `yield`
  separates startup from shutdown.
- `app.state` (and `request.state`) shares clients/pools set up at startup across
  request handlers.
- `APIRouter` modules mounted via `app.include_router(router, prefix=...)`
  organize routes by feature under a shared prefix. `include_router` also takes
  `tags`, `dependencies` and `responses`, and applies them without mutating the
  router, so one router can be mounted twice with different settings. The
  prefix carries no trailing `/`.
- Dependencies run in a fixed order: those passed to `include_router` first,
  then those on the path decorator, then the parameter dependencies.
- `StreamingResponse(generator, media_type="text/event-stream")` emits
  Server-Sent Events.
- `fastapi.testclient.TestClient` drives the app in-process and requires the
  `httpx` package to be installed.

## Idioms & best practices
- Pick `def` or `async def` per handler by what it calls. Use `async def` when
  the library it calls is awaited, or when the handler does no I/O at all. Use
  plain `def` when the library blocks and offers no `await`, which is still
  true of many database drivers. Upstream's own default when unsure is plain
  `def`, because then the framework does the offload.
- Declaring every handler `async def` is allowed, but it turns the framework's
  threadpool guarantee into a per-handler duty: each blocking call reachable
  from any handler must be offloaded by hand. The offload rule itself lives in
  `../language/python.md`.
- Keep shared dependencies (authentication, database sessions) in their own
  module, and attach cross-cutting ones once at `include_router`.
- Open and close pooled resources (DB pools, caches) in `lifespan` rather than
  in per-event startup/shutdown handlers, storing them on `app.state`.
- For SSE behind a buffering proxy, send `Cache-Control: no-cache` and
  `X-Accel-Buffering: no` headers to disable proxy buffering of the stream.
- Put tests in files separate from the application and write them as plain
  `def` functions that call `TestClient` without `await`. A suite that runs
  pytest in an async mode is on upstream's separate async-testing footing, and
  the plain-`def` guidance does not describe it.

## General pitfalls
- A blocking call inside an `async def` handler stalls every concurrent request
  on that worker. The framework does not catch it, and common linters do not
  either, so it shows up as latency under load.
- Authentication attached at mount time is invisible at the route. Reading a
  router module tells you nothing about whether its routes are protected; the
  answer is one keyword argument where the router is mounted. A router mounted
  without that argument, or one whose mount line was copied from a public
  router, serves its routes open and looks identical in its own file. Add a test
  that enumerates `app.routes` and asserts every route outside an explicit
  public allowlist resolves the authentication dependency. If the dependency can
  be switched off by configuration, also assert that an unauthenticated request
  is rejected, since a resolved dependency that returns early protects nothing.
- An SSE change that keeps the generator but drops the no-buffering headers
  still passes a status-code assertion, and the stream silently buffers behind
  the proxy. Assert the headers, not only the status.

## Upstream docs
- Docs: https://fastapi.tiangolo.com
- Concurrency (`def` vs `async def`): https://fastapi.tiangolo.com/async/
- Routers and dependency order: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Testing: https://fastapi.tiangolo.com/tutorial/testing/
- Repo: https://github.com/fastapi/fastapi
