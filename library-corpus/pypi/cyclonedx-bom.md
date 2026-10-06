# cyclonedx-bom — pypi

> Project-agnostic surface notes, kept in the seed's library corpus
> (`library-corpus/README.md`). Orientation for a library, not a record of one
> project's versions: for exact pins, CVEs, and per-release behavior, run
> `ingest-library` against the project's own lockfile.

## What it is
`cyclonedx-bom` is the CycloneDX project's software bill of materials (SBOM)
generator for Python. It reads a Python dependency set and writes a CycloneDX
document listing each component, its version and its package URL, for
supply-chain and vulnerability tooling to consume.

One project carries three names, and each is load-bearing:

| Where | Name |
|---|---|
| PyPI distribution (what `pip install` takes) | `cyclonedx-bom` |
| Command it installs (what every invocation uses) | `cyclonedx-py`, also `python -m cyclonedx_py` |
| Upstream repository (changelog, issues, advisories) | `CycloneDX/cyclonedx-python` |

The document model underneath is a separate library, `cyclonedx-python-lib`.

## Install, setup and configuration
- `pip install cyclonedx-bom` (or `pipx` / `uv tool`), at an exact pin, in an
  environment separate from the application when possible. The command is
  `cyclonedx-py`.
- Options are per subcommand (input, output file, format, spec version). The
  spec version has a default that moves
  between tool majors, so pass `--schema-version` explicitly when a consumer
  expects a particular one.

## Core API / usage shape
- It is a command-line tool. Install it with `pip`, `pipx` or `uv tool`, into an
  environment separate from the application when possible.
- The subcommand names the input source:
  - `cyclonedx-py environment` (aliases `env`, `venv`) reads an installed Python
    environment;
  - `cyclonedx-py requirements` reads pip requirements files;
  - `cyclonedx-py pipenv` and `cyclonedx-py poetry` read those tools' manifests
    and lockfiles.
- Output file, output format (JSON or XML) and CycloneDX spec version are
  switches on each subcommand; read `cyclonedx-py <subcommand> --help` for the
  installed version's spelling.

## Idioms & best practices
- Record all three names on first ingest and search for all three. Grepping for
  one and concluding the tool is absent is the "different name, same thing"
  trap.
- Generate the SBOM from the most exact input available. A lockfile or the real
  installed environment gives resolved versions; a loose requirements file gives
  ranges, and the SBOM inherits their vagueness.
- Pin the generator exactly in the image or tool environment that produces
  evidence. An SBOM from a different generator version is not directly
  comparable to the one before it.
- Installing it with `pip install --require-hashes` means hashing its whole
  transitive closure (it pulls `cyclonedx-python-lib` and that library's own
  dependencies), not only the top-level package.
  `tool-corpus/ops/hashed-lock-closure-check.md` checks that a lock covers it.
  When it shares an image with other scanners, lock their closures together:
  the shared-closure rule lives on `library-corpus/pypi/bandit.md`.

## General pitfalls
- A missing command that a wrapper downgrades to a warning is a silent missing
  SBOM. If a preflight finds no `cyclonedx-py` on `PATH`, prints a warning, skips
  the Python component and exits 0, the pipeline reports success with one SBOM
  absent. Fail the step when the tool is missing, and assert each expected SBOM
  file exists.
- A generator version bump changes the artifacts (fields, component
  identifiers, spec version). Regenerate and diff before moving the pin.
- Installing it into a Debian-family image's system Python meets PEP 668; the
  `pypi/pyyaml.md` page owns that trap and the correct install patterns.

## Testing
- Assert that each expected SBOM file exists, parses, and lists the components
  you know are installed; a missing or empty SBOM must fail the step (pitfalls
  above).
- Regenerate and diff before a generator bump, so a changed artifact is a
  reviewed change.

## Security defaults
- The SBOM is only as exact as its input: a loose requirements file yields
  version ranges (idioms above). This page has no confirmed source on whether
  a subcommand reaches the network.

## Operational behaviour
- The `environment` subcommand describes an installed Python environment, so
  it runs where that environment is (inside the image that ships it, for
  example).

## Interop
- The output is a CycloneDX document (JSON or XML) for supply-chain and
  vulnerability tools that read the CycloneDX specification.
- Often installed with `bandit` and other scanners
  (`library-corpus/pypi/bandit.md`).

## Major lines

### Before 4.x
- The deprecated `cyclonedx-bom` entry point still exists, and the input source
  is chosen with flags (`-e` for the environment, `-r -i <file>` for
  requirements, `-p` / `-pip` with a lockfile for Poetry and Pipenv); Conda
  lockfiles are read.

### 4.x and later
- Not backwards compatible: nearly all behaviour changed. The `cyclonedx-bom`
  entry point is removed (use `cyclonedx-py`, or `python -m cyclonedx_py`);
  each source is a subcommand; Poetry and Pipenv take a project directory
  instead of a lockfile; Conda lockfile analysis is removed (Conda Python
  environments work through `environment`); the schema version is set with
  `--schema-version` per subcommand. Upstream keeps an "Upgrading to v4" guide.

## Upstream docs
- Docs: https://cyclonedx-bom-tool.readthedocs.io/
- Subcommands and aliases: https://cyclonedx-bom-tool.readthedocs.io/en/latest/usage.html
- Repo: https://github.com/CycloneDX/cyclonedx-python
- Package: https://pypi.org/project/cyclonedx-bom/
- Specification: https://cyclonedx.org/specification/overview/
