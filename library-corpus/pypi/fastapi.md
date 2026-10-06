# fastapi — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`fastapi` is an ASGI web framework for building HTTP APIs with Python type hints,
Pydantic models for request/response validation, dependency injection, and
automatic OpenAPI docs.

## Install, setup and configuration
- `pip install fastapi` (the `fastapi[standard]` extra adds the commonly used
  server and tooling). FastAPI runs under an ASGI server; uvicorn is the usual
  one.
- `uvicorn.run(app_object)` cannot use `reload=True` or `workers=N`: both need
  the import string form, `uvicorn.run("pkg.mod:app", ...)`, inside an
  `if __name__ == "__main__":` block. `--reload` and `--workers` are mutually
  exclusive.
- Upstream's versioning advice: pin FastAPI to a range that admits one minor,
  as upstream's own example does, add tests, then raise the pin.
  It says not to pin Starlette, because each FastAPI release selects the
  Starlette version it needs.
- Observed in practice: HTTP-layer security fixes often land in Starlette, so
  some projects declare a Starlette floor (a minimum, never an exact pin) to
  pick them up. That goes past upstream's "don't pin Starlette" advice; a floor
  that conflicts with FastAPI's own requirement makes the install fail, which is
  the signal to bump FastAPI.

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
- `app.mount(path, subapp)` attaches an independent ASGI application. A
  mounted FastAPI sub-app serves its own OpenAPI schema and docs UI under the
  mount path, and its routes are absent from the root schema; `include_router`
  instead merges routes into one schema.
- `StreamingResponse(generator, media_type="text/event-stream")` emits
  Server-Sent Events.
- Attach the response model with `response_model=` or the return annotation.
  A model built only inside the handler is validated when it is constructed but
  adds nothing to the OpenAPI schema.

## Idioms & best practices
- Pick `def` or `async def` per handler by what it calls. Use `async def` when
  the library it calls is awaited, or when the handler does no I/O at all. Use
  plain `def` when the library blocks and offers no `await`, which is still
  true of many database drivers. Upstream's own default when unsure is plain
  `def`, because then the framework does the offload.
- Upstream's case for `async def` on compute-only handlers covers "trivial
  compute-only" work, where plain `def` would gain only about 100
  nanoseconds.
  Observed in practice: numeric work measured in milliseconds is the blocking
  case, so declare such a handler `def`.
- Type the request body with a model. `payload: dict = Body(...)` throws away
  request validation and leaves the OpenAPI request schema opaque.
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
- Observed in practice: an `async def` that awaits a coroutine which never
  yields is decoration. The loop is held throughout, and health probes queue
  behind it, so the first symptom is often failing health checks.
- Threadpool offload frees the loop but adds no CPU. A CPU-bound endpoint in
  one process still serializes; scale it with processes (workers).
- Observed in practice: a model built inside a handler raises its
  `ValidationError` there, and a broad `except` around the handler body
  swallows it.
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

## Testing
- `fastapi.testclient.TestClient` drives the app in-process and requires the
  `httpx` package to be installed. Write tests as plain `def` functions that
  call it without `await` (the async-testing footing is separate, as above).
- `app.dependency_overrides[dep] = fake` swaps a dependency for a test.
- Test the route table itself (every non-public route resolves the
  authentication dependency), not only individual handlers.

## Security defaults
- Nothing is protected by default: authentication is a dependency you attach,
  per route or at `include_router` (the mount-time pitfall above).
- Request bodies are validated only as far as their declared types; a `dict`
  body accepts anything.
- The OpenAPI schema and docs UIs are served by default; a deployment that
  should not publish them sets `openapi_url=None` (or the docs URLs to `None`).

## Operational behaviour
- Startup and shutdown run in `lifespan`. Plain `def` handlers share a
  threadpool; `async def` handlers share the event loop.
- One worker process runs one event loop. CPU-bound work needs more processes
  (`--workers`, or a process manager), not more threads.

## Interop
- Request and response models are pydantic models
  (`library-corpus/pypi/pydantic.md`); when pydantic arrives only through
  FastAPI, declare it yourself if you rely on its behaviour.
- The routing, middleware, `TestClient` and responses come from Starlette.
- The offload rule for blocking calls is on `library-corpus/language/python.md`.

## Major lines
FastAPI is pre-1.0. Upstream says breaking changes and new features land in
minor versions, so the minor is the breaking boundary. Its docs site is
unversioned and describes the current release, not your pin.

### Lines before 0.100 (Pydantic v1)
- Models, validators and `response_model` behaviour follow Pydantic v1.

### 0.100 and later (Pydantic v2)
- FastAPI supports Pydantic v2 from this line on, and for a while it accepts
  either v1 or v2. A later minor drops Pydantic v1 (it keeps only temporary
  support for v2's `pydantic.v1`). Model code follows the v2 API on the
  pydantic page. Upstream keeps a migration recipe from Pydantic v1 to v2.

## Upstream docs
- Docs: https://fastapi.tiangolo.com
- Concurrency (`def` vs `async def`): https://fastapi.tiangolo.com/async/
- Routers and dependency order: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Testing: https://fastapi.tiangolo.com/tutorial/testing/
- Repo: https://github.com/fastapi/fastapi
