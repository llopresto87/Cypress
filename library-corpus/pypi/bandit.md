# bandit — pypi

> Project-agnostic, version-durable surface notes, folded into CYPRESS by the
> harvest protocol. Orientation for a library, NOT a version-pinned page — for
> exact pins, CVEs, and per-release behavior, run `ingest-library` against the
> project's own lockfile.

## What it is
`bandit` is a static application security testing (SAST) tool for Python source,
maintained by PyCQA. It parses each file into an abstract syntax tree, runs a set
of security checks (plugins, each with a test ID such as `B602`) over it, and
reports every finding with a severity and a confidence rating. It reads code; it
never runs it.

## Core API / usage shape
- It is used as a command-line tool, typically installed into a tool
  environment (`pipx`, `uv tool`) and kept out of the application's own
  dependencies.
- `bandit -r <path>` scans a tree recursively. `-f` selects the report format
  (for example `json`) and `-o` writes the report to a file.
- Optional features ship as pip extras, and each one gates a capability:
  - `bandit[toml]` lets it read a `[tool.bandit]` section from `pyproject.toml`.
    The file is not discovered on its own; pass it with `-c pyproject.toml`.
  - `bandit[sarif]` adds the SARIF output format consumed by code-scanning
    dashboards.
  - `bandit[baseline]` installs the separate `bandit-baseline` command. The
    core `-b`/`--baseline <report>` option needs no extra: it compares the run
    against a saved JSON report, so only new findings surface.
- Severity and confidence filters (`--severity-level`, `--confidence-level`, or
  the repeated `-l` / `-i` short forms) report only issues at that level or
  higher, which cuts the report to what a gate acts on.
- `--exit-zero` exits 0 "even with results found", which suits an advisory
  report and defeats a gate. Upstream's option reference states no exit status
  for findings otherwise, so a gate proves once, on its pinned version, that a
  planted finding fails the step.
- A `# nosec` comment suppresses findings on its line. Naming the checks,
  `# nosec B602, B607` (or the full test name), suppresses only those and
  leaves the rest of the line scanned.

## Idioms & best practices
- Install exactly the extras your pipeline consumes, and treat each one as a
  requirement: a SARIF-publishing pipeline needs `[sarif]`, a pyproject-configured
  scan needs `[toml]`.
- Prefer ID-scoped `# nosec <ID>` over a bare `# nosec`, and give each
  suppression a reason nearby, so a reviewer can tell a judged false positive
  from a silenced one.
- Keep the scanner at an exact pin inside the scanning image or tool
  environment. Reports from different scanner versions are not directly
  comparable.
- Installing it into a Debian-family image's system Python meets PEP 668; the
  `pypi/pyyaml.md` page owns that trap and the correct install patterns.

## General pitfalls
- A missing extra can turn into a silent hole in the evidence. A wrapper script
  that checks for SARIF support, prints a warning when it is absent, and still
  exits 0 produces a green scan step with no SAST report behind it. A later image
  rebuild that drops the extra to save space fails no test. Make the wrapper
  fail when the scanner or a required extra is missing, and assert the report
  file exists and parses.
- A scanner version bump changes the findings, because checks are added and
  tuned between releases. Re-run the full scan and diff the reports before
  moving the pin, so a new finding is triaged and not mistaken for a code
  regression, and a vanished one is not mistaken for a fix.
- Findings are pattern-based, so expect false positives (and false negatives).
  A clean report means none of the implemented checks matched, not that the
  code is secure.

## Upstream docs
- Docs: https://bandit.readthedocs.io/
- Configuration and `# nosec`: https://bandit.readthedocs.io/en/latest/config.html
- Command-line options (`-b`, `-l`/`-i`, `--severity-level`, `--exit-zero`):
  https://bandit.readthedocs.io/en/latest/man/bandit.html
- Extras (`toml`, `baseline`, `sarif`): https://bandit.readthedocs.io/en/latest/start.html
- Repo: https://github.com/PyCQA/bandit
- Package: https://pypi.org/project/bandit/
