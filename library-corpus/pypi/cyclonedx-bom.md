# cyclonedx-bom — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

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

## Upstream docs
- Docs: https://cyclonedx-bom-tool.readthedocs.io/
- Subcommands and aliases: https://cyclonedx-bom-tool.readthedocs.io/en/latest/usage.html
- Repo: https://github.com/CycloneDX/cyclonedx-python
- Package: https://pypi.org/project/cyclonedx-bom/
- Specification: https://cyclonedx.org/specification/overview/
