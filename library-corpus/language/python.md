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
  concurrent awaitables.
- The interpreter is often provisioned via a Docker base image pinned to a minor
  line:

  ```dockerfile
  FROM python:<minor>-slim
  ```

  A bare minor tag names a line, not a patch — a mutable tag in the ordinary
  Docker sense (see the `container/docker` page).
- The `-slim` variant is Debian-based, substantially smaller than the full
  image, and omits the build toolchain and many system libraries.
- PEP 604 union syntax (`X | None`) is the modern type-annotation style.

## Idioms & best practices
- Never call a blocking client from `async` code. Use the library's async client
  where one exists; otherwise run the sync call in a worker thread and hand
  results back to the loop.
- Prefer `-slim` (or distroless) base images to reduce image size, adding only
  the system libraries a given dependency actually needs.
- Pin a specific patch-level image tag (or a lockfile / `.python-version` /
  `runtime.txt`) when you need a reproducible, known interpreter patch — a bare
  minor tag leaves the patch level indeterminate.

## General pitfalls
- `-slim` images ship without a compiler toolchain — the Python instance of the
  general "a minimal base lacks the tools you assume" trap on the
  `container/docker` page. Packages that ship prebuilt wheels install fine, but
  any dependency that compiles at install time needs build tooling added
  explicitly.
- Floating minor tags mean the running interpreter's patch level (and thus which
  patch-level fixes it contains) is not knowable from the Dockerfile alone.
- Standard-library modules are removed across major/minor lines (e.g. PEP 594's
  removal of legacy "dead battery" modules), so code relying on old stdlib
  modules can break on upgrade.

## Upstream docs
- https://docs.python.org/3/ — official Python documentation
- https://www.python.org/ — Python homepage and downloads
