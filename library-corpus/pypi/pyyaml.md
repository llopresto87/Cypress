# pyyaml — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
PyYAML is the standard YAML parser and emitter for Python, imported as `yaml`.
It reads YAML into ordinary Python objects (dicts, lists, scalars) and writes
them back out, and it is what most Python tooling reaches for whenever a
configuration file, a manifest, a compose file, or a pipeline definition has to
be read.

**It is not a standard-library module.** It merely behaves like one, because it
is present on most Linux hosts as a dependency of system tooling — which is
exactly what makes an undeclared `import yaml` look safe right up to the host
where it is not.

- **PyPI package:** `pyyaml`; **import name:** `yaml` (they differ — a
  requirements line and an import statement do not match by spelling).
- On Debian/Ubuntu-family systems the same library is also packaged as the OS
  package `python3-yaml`, which is a different install path with different
  rules (see the PEP 668 pitfall below).

## Core API / usage shape
```python
import yaml

data = yaml.safe_load(text)              # one document -> Python objects
docs = list(yaml.safe_load_all(text))    # multi-document stream ("---")

out = yaml.safe_dump(data, sort_keys=False, default_flow_style=False,
                     allow_unicode=True)

try:
    yaml.safe_load(text)
except yaml.YAMLError as exc:            # base class for parse/scan errors
    ...
```
- `safe_load` / `safe_dump` restrict the tag set to standard YAML types.
  `yaml.load(stream, Loader=...)` takes an explicit loader —
  `SafeLoader`, `FullLoader`, or `UnsafeLoader`/`Loader` — and the choice of
  loader is the security decision.
- Emission is controlled by keyword arguments: `sort_keys`,
  `default_flow_style`, `indent`, `width`, `allow_unicode`,
  `explicit_start`.
- Custom types are wired with `add_constructor` / `add_representer` (or by
  subclassing `SafeLoader` / `SafeDumper` so the customization stays local
  rather than global).
- Anchors (`&name`), aliases (`*name`), and merge keys are parsed; the emitter
  emits anchors for shared object references.

## Idioms & best practices
- **Always `safe_load`.** Make the safe loader the default in every call site,
  and require an explicit, reviewed justification for anything else. A grep for
  `yaml.load(` that returns nothing is a cheap, durable invariant.
- **Declare the dependency even when the host already has it.** A manifest line
  costs nothing and is the only thing that distinguishes "we depend on this" from
  "it happened to be installed"; a comment in a test asserting the dependency
  exists is not a manifest.
- **Probe and fail loudly at the entry point** when a module is declared but
  installed out-of-band (an OS package, say). Check availability with
  `importlib.util.find_spec` — not a `try: import` — at the top of each entry
  point, and exit with a distinct, environment-class status and a message naming
  the exact install command. Four design choices worth reusing:
  1. `find_spec` keeps the diagnostic importable on the very host it exists to
     diagnose, and costs no parse time on a healthy run.
  2. The check belongs at the **entry point**, not as a guard around the library
     import, because real import chains are deferred — a guarded import speaks
     only once something reaches the config layer, minutes into a run, and is one
     edit away from being swallowed by a broad `except`.
  3. Use a distinct exit status meaning "the check could not run": a missing host
     package is not a repository fault, and sending the maintainer to edit a
     declaring file is the wrong-class remedy.
  4. **Derive** the in-scope entry-point set from the tree with a test rather than
     hand-listing it. A hand-written scope defined as "everything reaching the
     config layer" structurally excludes the one script that imports the library
     directly — and that script tends to run first.
- **Prefer `sort_keys=False`** when round-tripping human-authored files; the
  default reorders keys and turns a one-line change into an unreadable diff.
- **Emit deterministically** from any generator, since an emitted file is usually
  compared, committed, or hashed downstream.
- Reach for a round-trip-preserving library instead when comments and formatting
  must survive a read/modify/write cycle — PyYAML discards both by design.

## General pitfalls
- **Unsafe deserialization is the library's headline hazard.** `yaml.load` with a
  permissive loader can construct arbitrary Python objects from the document,
  which makes parsing an untrusted file equivalent to executing it. Treat any
  call site whose loader is not obviously safe as an open audit item rather than
  assuming either way.
- **Import placement is load-bearing safety, and nothing tests it.** Moving a
  deferred `import yaml` inside a surrounding `except Exception: return {}`
  converts a missing dependency into an empty configuration — and an empty
  configuration usually means "nothing is optional", so the program proceeds with
  silently wrong behavior instead of failing. The correctness lives in where the
  import sits, and a reviewer sees only a moved line.
- **Transitive presence is not a contract.** The library is commonly pulled in by
  distribution tooling on a normal server install, which is why an undeclared
  dependency survives for years; a slim base container image carries none of that
  closure (often not even an interpreter), so containerizing a host is exactly
  the moment every unguarded import breaks at once.
- **PEP 668 (`EXTERNALLY-MANAGED`) makes the obvious fix illegal** on modern
  distributions: a bare `pip install` into the system interpreter is refused by
  design. Two traps follow:
  - **`--user` is not an exemption.** The rule is that the installer must refuse
    for an externally-managed environment; the user-site install is refused too.
    Use a virtual environment, or the OS package.
  - **`--break-system-packages` is specifically dangerous here**, because the OS
    package is a hard dependency of system tooling — shadowing it with a
    pip-installed copy puts a non-distribution build underneath something the OS
    itself depends on, on a host where that matters.
  The correct pattern is the OS package at provisioning time, or a virtual
  environment, plus the fail-loud probe above.
- **An OS-package install means the version moves with the host**, not with any
  diff in the repository: a behavior change between distribution builds arrives
  unannounced. If that ever matters, the decision is whether to pin at all, and
  it is a decision, not a detail.
- **YAML's own sharp edges arrive through the parser**: unquoted `yes`/`no`/`on`/
  `off` and bare `y`/`n` can read as booleans, a leading-zero or colon-bearing
  token can read as a number or a time, an unquoted version-like string can read
  as a float, and tabs are not valid indentation. Quote anything whose type
  matters.
- **The install line can be the only thing holding a host together and be covered
  by nothing.** Provisioning scripts frequently have no automated test, so
  deleting the line that installs this library survives an entire test suite.

## Upstream docs
- Docs: https://pyyaml.org/wiki/PyYAMLDocumentation
- Repo: https://github.com/yaml/pyyaml
- PEP 668 / externally managed environments:
  https://packaging.python.org/en/latest/specifications/externally-managed-environments/
