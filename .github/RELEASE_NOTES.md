## 8.1.2 — a plant is ready to go from the get-go (2026-10-09)

After an install, a graft or a grow, the source index is already built, and
the owner reads in one short report what is set up and what still needs a
fix. Nothing is left to do by hand that the report does not name. A session
finds the tool through a seed skill, the kernel names it, and a question
about a file the plant owns loads that skill beside the node that owns the
file.

### The build report

- `install.sh` runs `python3 docs/graph/source-index.py build` as its last
  step, on every install that places files and so on every graft, and prints
  the report under `source index build (advice, never a failure of the
  install; ...)`. The build runs in isolated mode (`-I -B`) with stdin
  closed and a 120-second bound. An install never fails on it: when the
  build does not finish, one line says so and gives the command to run by
  hand.
- `tools/growth-audit.py` prints the same report after its verdicts, at
  every grow and graft. It is advice, never a verdict, and never sets the
  exit code; `--json` appends it as `{"source_index_report": [...]}`.
  `graft-run.py` keeps both copies, in `install.log` and `coverage.txt`.
- The report holds the cache line, the counts and the build time, then one
  record per setup gap, each with a `fix:` line under it: a `repo:` value
  that names nothing on disk (`repo-unresolved`), a Git repository inside
  the plant that no node names (`repository-unnamed`, new), a missing or
  empty test declaration (`no-test-declaration`, `no-test-files`), and the
  rest. Hints name files that look like tests but sit outside `TEST_GLOBS`,
  files in the test class that do not look like tests, and patterns in
  `docs/graph/source-index.json` that match no file
  (`config-pattern-unmatched`, with its own fix line).
- The cache bound, `CACHE_MAX_BYTES`, rises from 64 MiB to 196 MiB.

### Finding the tool

- A new seed skill, `skill.source-index` (`skills/source-index/SKILL.md`),
  is placed and projected like every seed skill. It sends the four
  questions (what depends on a file, which tests a change reaches, which
  pages cite a file, where a name is defined) to the tool, says how to act
  on the build report, and states the limit: an answer is a recommendation,
  and a file missing from it is never proof that the file is unaffected
  ([ADR-0030](docs/decisions/adr-0030-a-seed-tool-is-surfaced-by-a-seed-skill.md)).
  The seed now ships 16 skills; the Codex config example registers the new
  one, and the always-loaded surface on Claude Code grows to 25 800 bytes.
- The kernel's "Where to look next" gains one line for code questions:
  `python3 docs/graph/source-index.py --help` and `skill.source-index`.
  The owner raised `KERNEL_BUDGET` from 8 000 to 8 200 bytes for it.
- verify, canonize, grow and graft list the skill as a peer.

### The router

- When a task names a file that a plant node owns and also holds a trigger
  phrase of a seed skill, the router loads that skill beside the owning
  node, at most two skills (`PATH_TIER_SKILL_CAP`); a task that holds the
  phrases of more loads the node alone. Only skills the seed ships are
  added this way (SPEC-0002, ADR-0026 "Amendment, 8.1.2").
- A file path or a code name inside a trigger phrase no longer breaks it.
  A path stands in for the phrase's word `file` and a code name
  (`save_order`, `saveOrder`) for `name`, so "what breaks if I change
  src/app.py" holds `what breaks if I change this file`. An ordinary word
  still breaks a phrase.

### Graft and build output

- A graft now names an outdated seed page left in a plant (a file under
  `protocols/` or `method/` that the seed no longer ships, such as
  `protocols/toolcraft.md`) as RETIRED, and ties the graph-lint errors it
  causes to that page. It deletes nothing: the steward removes the page by
  name (migration (d)). A test graft on a copy of wrt-migration found the
  case.
- The build report's `Incomplete:` line stops at the row limit and ends
  with `and N more`; `--all` and `--json` show every row.
- Memory was measured near the 196 MiB cache bound: about 100,000 files,
  where a query needs about 1.3 GB.

### CI on macOS

- `tests/test-source-index.sh` checks how `repo:` values with different
  letter case are read only on a file system where case matters. It probes
  first and, on the macOS runner's case-insensitive disk, skips those two
  checks with a printed reason instead of failing.
