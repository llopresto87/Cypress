# python — language

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
Python is a general-purpose, dynamically-typed language with the CPython
reference interpreter and an extensive standard library. In containerized
projects the interpreter is commonly provisioned from the official Docker base
images (`python:<minor>` and its `-slim` variant).

## Install, setup and configuration
- Release cadence and support model: CPython follows a predictable annual
  release cadence (PEP 602), a new minor line every twelve months with ongoing
  patch releases. Each minor line gets about five years, a bugfix phase and then
  security-only fixes (the devguide's "versions" page lists each line's phase).
  NEP 29 and SPEC 0 recommend which floors downstream scientific projects
  support; they are not maintenance commitments.
- The interpreter is often provisioned via a Docker base image pinned to a minor
  line:

  ```dockerfile
  FROM python:<minor>-slim
  ```

  A bare minor tag names a line, not a patch: a mutable tag in the ordinary
  Docker sense (see the `container/docker` page).
- The `-slim` variant is Debian-based, substantially smaller than the full
  image, and omits the build toolchain and many system libraries.
- Prefer `-slim` (or distroless) base images to reduce image size, adding only
  the system libraries a given dependency actually needs.
- Pin a specific patch-level image tag (or a lockfile / `.python-version` /
  `runtime.txt`) when you need a reproducible, known interpreter patch. A bare
  minor tag leaves the patch level indeterminate.
- Multi-stage build: create the virtual environment in the full `python:<minor>`
  image, which has the toolchain, and copy `/opt/venv` into `-slim`. Keep the
  same absolute path and the same interpreter minor in both stages, because
  script shebangs and `pyvenv.cfg` hard-code both. Observed in practice. The
  `venv` docs call environments non-portable and not movable or copyable,
  because script shebangs hold absolute interpreter paths, and say to recreate
  one in its target location; they do not cover a copy between build stages.
- Keep the resolver out of the runtime image: install Poetry or pip-tools in a
  build-stage environment, export requirements, and install those with pip. The
  shipped image then holds neither resolver nor lockfile tooling. Observed in
  practice.
- Container environment: `PYTHONUNBUFFERED=1`, because stdout is
  block-buffered when it is not a terminal and logs otherwise arrive late or are
  lost on a crash. `PYTHONDONTWRITEBYTECODE=1` suits immutable images, at the
  cost of compiling on every start.

## Core API / usage shape
- `asyncio` is the standard concurrency model for I/O-bound code: coroutines
  share one event loop, so a blocking call made from `async` code stalls every
  other task on that loop. `asyncio.to_thread(...)` runs a blocking call on a
  worker thread (`loop.run_in_executor` does the same for code you must drive
  yourself, such as a synchronous generator); `asyncio.gather` fans out
  concurrent awaitables. Crossing the other way, from a worker thread back onto
  the loop, goes through `loop.call_soon_threadsafe()` or
  `asyncio.run_coroutine_threadsafe()`; the loop's other APIs are not
  thread-safe.
- PEP 604 union syntax (`X | None`) is the modern type-annotation style.
- Offload pools: threads (`asyncio.to_thread`, `ThreadPoolExecutor`) free the
  event loop, but the GIL keeps them from running pure-Python CPU work in
  parallel. `ProcessPoolExecutor` does run it in parallel. Compiled numeric
  kernels often release the GIL, so NumPy-heavy work can gain from threads
  (`library-corpus/pypi/numpy.md`).
- Script path versus `-m`: `python path/to/script.py` puts the script's own
  directory at `sys.path[0]`; `python -m pkg.mod` puts the current directory
  there. An import that resolves one way can fail the other, so the container
  command, the test configuration and local runs must use the same form.

## Idioms & best practices
- CPU-bound code is blocking too. The asyncio guide says "Blocking (CPU-bound)
  code should not be called directly": the cost is a delay across the whole
  loop, with no threshold below which it is fine.
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
  network I/O can themselves block the loop. Two signals appear even without
  debug mode: a coroutine called without `await` emits
  `RuntimeWarning: coroutine ... was never awaited`, and a task whose exception
  is never retrieved logs "Task exception was never retrieved" when it is
  garbage-collected. Outside production, run the `asyncio` logger at DEBUG and
  show `ResourceWarning` (`-X dev`, or `-W default`).
- Catch specific exceptions (PEP 8). `except Exception:` is the broadest form
  PEP 8 accepts, for program errors only; when a fallback is intended for a parse
  or validation failure, catch those errors and let the rest propagate or reach
  a separate, explicit `except Exception:`.
- Make the conventions executable: a configured linter, formatter and type
  checker in the repository, run by a gate. PEP 8 itself ranks consistency
  within a project above consistency with the guide, and without a tool nothing
  keeps either.
- **Measure a hash-locked closure for the target platform, from a clean slate.**
  `pip install --dry-run --report` leaves out every requirement the measuring
  environment already satisfies, so a lock built from its report can miss a
  package, and the hashed install then fails at build time. Add
  `--ignore-installed`, plus explicit target-platform, interpreter, ABI and
  `--only-binary=:all:` flags when the build targets a different platform from
  the one measuring.
- Raise one vulnerable transitive dependency in an image with
  `pip install --no-deps <pkg>==<version>`, then run `pip check`. That avoids
  re-resolving the whole tree, and `pip check` catches any declared requirement
  the raise breaks. Observed in practice. pip's docs describe the two parts
  only: `--no-deps` means "Don't install package dependencies", and `pip check`
  verifies that installed packages have compatible dependencies, exiting 1 when
  one does not. They do not describe the combination.
- Declare advisory-driven floors for transitive dependencies in the manifest,
  with a comment saying why. A floor that is never declared has nowhere to be
  raised from. Observed in practice; upstream is silent on advisory-driven
  floors.

## General pitfalls
- **`except (SpecificError, Exception)` is `except Exception` in disguise.**
  Every specific error subclasses `Exception`, so the first member of the tuple
  catches nothing the second would not. It reads in review as a narrow handler,
  and it turns an outage, a changed response shape and a refactoring bug into
  the same silent fallback.
- **`round()` is not half-up.** It rounds the binary float, and exact ties go
  to the even digit: `round(0.485, 2)` gives `0.48` because `0.485` is stored
  just below it, and `round(2.5)` gives `2`. Where a rule says half-up (money,
  scores, regulated figures), compute in `decimal.Decimal` built from a string
  with `quantize(..., rounding=ROUND_HALF_UP)`, and run the rule's worked
  example as a test.
- A linter suppression comment (`# noqa: <code>`) with no linter configuration
  in the tree is evidence that a linter once ran and has stopped. Treat the
  style, lint and type gates as absent, not as passing.
- `-slim` images ship without a compiler toolchain, the Python instance of the
  general "a minimal base lacks the tools you assume" trap on the
  `container/docker` page. Packages that ship prebuilt wheels install fine, but
  any dependency that compiles at install time needs build tooling added
  explicitly.
- Debian-family images mark the distro's own `python3` externally managed
  (PEP 668), so a bare `pip install` into it is refused. The official
  `python:*` images ship a separately built interpreter under `/usr/local`,
  which carries no such marker (PEP 668 leaves an unpatched upstream CPython
  unmarked). The `pypi/pyyaml` page
  owns the traps that follow and the correct patterns.
- Floating minor tags mean the running interpreter's patch level (and thus which
  patch-level fixes it contains) is not knowable from the Dockerfile alone.
- Standard-library modules are removed across major/minor lines (e.g. PEP 594's
  removal of legacy "dead battery" modules), so code relying on old stdlib
  modules can break on upgrade. The list for the 3.13 line is under major lines
  below.
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
- Stale bytecode: by default a `.pyc` is invalidated by comparing the source's
  modification time and size. A rewrite with the same size inside the same
  second is not recompiled, so the old code runs; this bites mutation testing
  and fast edit loops. Use `PYTHONDONTWRITEBYTECODE=1` with a cleared
  `__pycache__`, or hash-based pycs (PEP 552, `--invalidation-mode
  checked-hash`; `py_compile` already defaults to checked-hash when
  `SOURCE_DATE_EPOCH` is set). Observed in practice.
- A `pip freeze` snapshot that nothing installs from (a regenerated
  `constraints.txt`, say) goes stale and misleads readers about the pins.
  Check what the build actually installs from. Observed in practice. pip's docs
  say `pip freeze` reports what is installed and does not compute a lockfile;
  they say nothing about a snapshot going stale.
- In a multi-stage image, the full and slim stages name two moving tags that
  resolve independently, so one build can mix patch levels of the same minor.
  Pin both stages. Observed in practice; the image documentation is silent on
  mixing tags across stages.
- Some scientific and ML wheels load OpenMP (`libgomp1`) or other system
  libraries at import time, and `-slim` lacks them. The failure is an
  `ImportError` at service start, not at build; add the library in the runtime
  stage. Observed in practice. The image documentation says only that `-slim`
  holds the minimal Debian packages needed to run Python; it does not name
  runtime libraries that wheels load.
- On Alpine (musl), many scientific wheels are glibc-only or lag behind, which
  forces source builds. Prefer the glibc `-slim` base for the numeric stack.
  Observed in practice. The image documentation warns in general terms that
  the Alpine variant uses musl libc, so software often runs into issues
  depending on its libc assumptions.

## Testing
- `python -m unittest discover -s <dir>` puts the start directory on
  `sys.path`. A test that imports a sibling helper passes under discover and
  fails when run alone as a dotted module; `-t <top>` needs `__init__.py`
  packages along the path. Observed in practice.
- An error in `setUpClass` or `setUpModule` suppresses the tests it guards: the
  suite reports a lower total and a few errors. A dropped test count usually
  means one setup error, not many regressions. Observed in practice.
- A `sitecustomize.py` placed on `PYTHONPATH` in a temporary directory runs at
  the start of every child interpreter, so a test can watch child Python
  processes without touching the code under test. Observed in practice. The
  `site` docs say `site` imports `sitecustomize` during initialization, unless
  the interpreter starts with `-S`; they do not describe it as a test probe.
- A test that mocks `urlopen` cannot see redirect handling (pitfall above); use
  a real loopback server pair.
- The stale-bytecode trap above matters most to mutation testing: a mutant that
  never recompiles never runs.

## Security defaults
- `urllib` follows redirects and carries `Authorization` across them (pitfall
  above).
- `pickle`, `eval` and `exec` run code from their input, so untrusted data must
  never reach them.
- PEP 668 keeps `pip` out of a distribution-managed interpreter (pitfall above);
  use a virtual environment rather than `--break-system-packages`.

## Operational behaviour
- One interpreter process runs Python bytecode on one thread at a time (the
  GIL), so CPU-bound scaling comes from processes; I/O-bound code scales with
  asyncio or threads (core API above).
- A minimal image without `curl` can still health-check over HTTP:
  `python -c "import urllib.request; urllib.request.urlopen(URL, timeout=5)"`.
  Observed in practice. The `urllib.request` docs back the exit status: the
  default opener turns HTTP error responses into `HTTPError` and raises
  `URLError` on protocol errors, so the command exits non-zero on failure.
- Logs reach the collector promptly only with unbuffered stdout
  (`PYTHONUNBUFFERED=1`, install above).

## Interop
- Numeric stacks move together across interpreter and library upgrades
  (`library-corpus/pypi/numpy.md`, `library-corpus/pypi/scipy.md`).
- The `-slim` and Alpine traps above decide which base image a native
  dependency can use (`library-corpus/container/docker.md`).

## Major lines

### 3.13 line
- PEP 594 is complete: `aifc`, `audioop`, `cgi`, `cgitb`, `chunk`, `crypt`,
  `imghdr`, `mailcap`, `msilib`, `nis`, `nntplib`, `ossaudiodev`, `pipes`,
  `sndhdr`, `spwd`, `sunau`, `telnetlib`, `uu` and `xdrlib` are removed, along
  with `lib2to3` and the `2to3` tool and `tkinter.tix`.

### 3.14 line
- `concurrent.futures.InterpreterPoolExecutor` runs work in subinterpreters,
  a third offload pool beside threads and processes.

## Upstream docs
- https://docs.python.org/3/: official Python documentation
- https://docs.python.org/3/library/asyncio-dev.html: developing with asyncio
  (blocking code, thread safety, debug mode)
- https://docs.python.org/3/library/functions.html#round and
  https://docs.python.org/3/library/decimal.html: `round()` and `Decimal`
  rounding modes
- https://peps.python.org/pep-0008/: PEP 8, the style guide
- https://www.python.org/: Python homepage and downloads
