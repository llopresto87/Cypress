# python — language

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
Python is a general-purpose, dynamically-typed language with the CPython
reference interpreter and an extensive standard library. In containerized
projects the interpreter is commonly provisioned from the official Docker base
images (`python:<minor>` and its `-slim` variant).

## Core API / usage shape
- CPython follows a predictable annual release cadence: a new minor line each
  year, with ongoing patch releases and a defined support/maintenance window per
  line.
- `asyncio` is the standard concurrency model for I/O-bound code: coroutines
  share one event loop, so a blocking call made from `async` code stalls every
  other task on that loop. `asyncio.to_thread(...)` runs a blocking call on a
  worker thread (`loop.run_in_executor` does the same for code you must drive
  yourself, such as a synchronous generator); `asyncio.gather` fans out
  concurrent awaitables. Crossing the other way, from a worker thread back onto
  the loop, goes through `loop.call_soon_threadsafe()` or
  `asyncio.run_coroutine_threadsafe()`; the loop's other APIs are not
  thread-safe.
- The interpreter is often provisioned via a Docker base image pinned to a minor
  line:

  ```dockerfile
  FROM python:<minor>-slim
  ```

  A bare minor tag names a line, not a patch: a mutable tag in the ordinary
  Docker sense (see the `container/docker` page).
- The `-slim` variant is Debian-based, substantially smaller than the full
  image, and omits the build toolchain and many system libraries.
- PEP 604 union syntax (`X | None`) is the modern type-annotation style.

## Idioms & best practices
- Never call a blocking client from `async` code. Use the library's async client
  where one exists; otherwise run the sync call in a worker thread and hand
  results back to the loop.
- **Enforce a sync-only contract; do not just write it down.** A function that
  must only run inside `to_thread` is usually documented with a comment, and
  nothing fails when a later caller invokes it straight from a handler. Assert
  it instead: check for a running loop on entry (`asyncio.get_running_loop()`
  raises when there is none), or pin it with a characterization test.
- Use asyncio debug mode outside production: `PYTHONASYNCIODEBUG=1`, Python
  Development Mode, `asyncio.run(..., debug=True)` or `loop.set_debug()`. It
  raises on non-thread-safe calls from the wrong thread and logs every callback
  slower than 100 ms (`loop.slow_callback_duration`), which makes it the
  cheapest detector for a blocking call on the loop. Log handlers that do
  network I/O can themselves block the loop.
- Catch specific exceptions (PEP 8). `except Exception:` is the broadest form
  PEP 8 accepts, for program errors only; when a fallback is intended for a parse
  or validation failure, catch those errors and let the rest propagate or reach
  a separate, explicit `except Exception:`.
- Make the conventions executable: a configured linter, formatter and type
  checker in the repository, run by a gate. PEP 8 itself ranks consistency
  within a project above consistency with the guide, and without a tool nothing
  keeps either.
- Prefer `-slim` (or distroless) base images to reduce image size, adding only
  the system libraries a given dependency actually needs.
- Pin a specific patch-level image tag (or a lockfile / `.python-version` /
  `runtime.txt`) when you need a reproducible, known interpreter patch. A bare
  minor tag leaves the patch level indeterminate.
- **Measure a hash-locked closure for the target platform, from a clean slate.**
  `pip install --dry-run --report` leaves out every requirement the measuring
  environment already satisfies, so a lock built from its report can miss a
  package, and the hashed install then fails at build time. Add
  `--ignore-installed`, plus explicit target-platform, interpreter, ABI and
  `--only-binary=:all:` flags when the build targets a different platform from
  the one measuring.

## General pitfalls
- **`except (SpecificError, Exception)` is `except Exception` in disguise.**
  Every specific error subclasses `Exception`, so the first member of the tuple
  catches nothing the second would not. It reads in review as a narrow handler,
  and it turns an outage, a changed response shape and a refactoring bug into
  the same silent fallback.
- A linter suppression comment (`# noqa: <code>`) with no linter configuration
  in the tree is evidence that a linter once ran and has stopped. Treat the
  style, lint and type gates as absent, not as passing.
- `-slim` images ship without a compiler toolchain, the Python instance of the
  general "a minimal base lacks the tools you assume" trap on the
  `container/docker` page. Packages that ship prebuilt wheels install fine, but
  any dependency that compiles at install time needs build tooling added
  explicitly.
- Debian-family images mark the system interpreter externally managed
  (PEP 668), so a bare `pip install` into it is refused. The `pypi/pyyaml` page
  owns the traps that follow and the correct patterns.
- Floating minor tags mean the running interpreter's patch level (and thus which
  patch-level fixes it contains) is not knowable from the Dockerfile alone.
- Standard-library modules are removed across major/minor lines (e.g. PEP 594's
  removal of legacy "dead battery" modules), so code relying on old stdlib
  modules can break on upgrade.
- **`urllib` follows redirects, and a test that patches `urlopen` cannot see
  it.** The default opener follows a 3xx, and its redirect handler copies the
  request's headers, `Authorization` included, onto the redirected request
  (only those added with `add_unredirected_header` stay behind).
  Refusing redirects when a credential rides the request is owned by
  `tool-corpus/ops/declared-variable-existence-auditor.md` ("Hard refusal to
  follow redirects"). What is specific to `urllib` is the test: a mock of
  `urllib.request.urlopen` never runs the opener's handlers, so it passes while
  the refusal is broken. Only a real pair of loopback servers, one answering
  302 to the other, exercises the redirect handler.

## Upstream docs
- https://docs.python.org/3/: official Python documentation
- https://docs.python.org/3/library/asyncio-dev.html: developing with asyncio
  (blocking code, thread safety, debug mode)
- https://peps.python.org/pep-0008/: PEP 8, the style guide
- https://www.python.org/: Python homepage and downloads
