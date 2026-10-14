## 8.2.0 — a harvest folded back into the seed (2026-10-14)

This release comes from a harvest: what grown plants learned, made generic
and folded back into the seed. The seed now needs Python 3.14 and says so at
install time. Graft and grow commit the plant before they write. A team can
keep its own `AGENTS.md`. Generic skill pages reach a plant when its work
needs them, and every agent runs its own route. The corpora gain library,
tool, skill and legal pages. Project names that earlier records carried are
recast generically; the disclosure is below.

### Python 3.14

- The seed's minimum Python is 3.14, and SPEC-0005 §5 is the one home of
  that figure. Every script the installer places and every hook it wires
  runs on it.
- `install.sh` runs on `python3` when it is at 3.14 or newer, else on the
  first `python3.<n>` at or above it on `PATH`, and writes that name into
  every hook command, the Prime Agent extensions included. With none on
  `PATH` it refuses before writing anything, with the fix in one line. When
  `python3` itself is older, a NEXT STEP says so, because agent sessions run
  the graph tools as `python3 docs/graph/<tool>.py`.
- `install.sh --check` runs each wired hook on the interpreter the hook
  names. The CI gate runs on Python 3.14, and `tests/test-tool-help.sh`
  holds the installer's `PYTHON_FLOOR`, the spec line and the CI version
  equal.

### The installer

- A run that made backups ends with a BACKUPS block: every installer backup
  in the plant, one line per date with its count, and a reminder to stage
  by explicit path, never with `git add -A` or `git add .`.
- When the plant is its own Git repository and ignores `.cypress/seed.json`,
  the installer prints the `.gitignore` lines that keep the stamp and the
  coverage record tracked. It never edits `.gitignore`.
- A stamp key an earlier seed wrote and this one no longer reads is named
  and kept.
- `--kernel-mode compose` keeps a team's own `AGENTS.md` canonical: the
  installer never writes it, and `CLAUDE.md` imports it on its first line
  and carries the kernel after it. The cost, stated on every run: a host
  that reads only `AGENTS.md` (opencode, Prime Agent, Codex, Copilot) never
  sees the kernel. The mode is recorded in the stamp as `kernel_mode`;
  `--kernel-mode replace`, the default, returns to one shared kernel body.
  The installer refuses compose before writing when `AGENTS.md` is missing,
  a symbolic link, or a body the seed wrote. `graft-audit.py` reads a
  compose-mode plant.
- A crashed router is one line in the session, `No route: graph-lint.py
  exit <status>: <its last stderr line>`, and the prompt still goes through
  (SPEC-0003).
- `--expertise skill-corpus/<name>` places a generic skill page as the
  routable node `docs/graph/skills/<name>.md`. Every skill-corpus page now
  carries node frontmatter, and the installer refuses a page without it by
  name.
- A placed corpus page needs no row in the plant's `index.md`: the plant's
  `graph-lint.py` reads `origin: corpus@<version>` as an entry point
  (SPEC-0001 PLACED_CORPUS_PAGE_IS_REACHABLE).
- The matcher proposes the Microsoft Graph platform page for the Graph SDK
  packages.

### Graft, grow and harvest

- Graft makes the baseline commit itself before its first write, per the
  plant's version-control shape: one commit of the tree as found in the
  plant's own repository, staged by explicit path, or a `.gitignore` and
  `git init` where the plant has no repository of its own. It commits a
  checkpoint after a ratified flag flip, after the apply, after each remedy
  that re-runs the installer and at the end, and records each commit.
  Nested repositories stay read-only. It never fetches, switches or pushes.
- Graft lists the backups by date for the owner's decision on which to
  keep, offers compose mode to a plant that keeps its own hub, and records
  the owner's own words for a plant fact beside the value.
- Graft and grow read what the plant needs (its recurring procedures, the
  tools and services it drives) as well as what its manifests name, and
  propose the corpus page that serves each need with the path that shows
  it.
- `graft.gate.routes` records a plant's own adversarial routing baseline
  with `agent-lint.py --eval --record-baseline` at the graft that brings
  the routing corpus or changes the roster, and gates the plant on it. The
  seed's roster keeps its budget.
- Grow commits a baseline before its first write and a checkpoint at the
  close of every phase that wrote, and `grow.gate.write-scope` reads each
  phase against the commit that opened it. A corrections record takes what
  authors find after the evidence ledgers freeze, and outranks them. An
  owner-stated fact no file witnesses is recorded once, labelled, with the
  owner's words.
- Harvest's check that a plant was left untouched compares content hashes
  of dirty, untracked and read ignored files, so a write to a file that was
  already dirty is caught. A harvest that re-reads a plant it already read
  takes a fast path, and its agnosticism check takes `--forbid-file`.

### Doctrine

- Two new delegation leaves: `delegation-wave-integrity.md` (each worker's
  write set in a table, a wave baseline, output that survives an
  interrupted spawn) and `delegation-continuation.md` (when to resume an
  agent that already handed back, and when to brief a fresh one).
- Every worker runs its own route. Architect, product, devil's advocate,
  UI/UX designer and legal gain Bash, which their charters limit to lookup
  and measurement; legal's shell never reaches the network. A worker brief
  no longer carries a closure the caller routed.
- The graph-session bootstrap gains two steps: check the route against the
  files about to be touched, and leave shared git state alone.
- In an operations or verification pass, the tester lists each bug it
  finds, root-caused, and the fix waits for the owner's go-ahead. Outside
  such a pass the default stands.
- A project's own authorization levels and the seed's tiers are two axes;
  the stricter wins, and neither is translated into the other.
- Decision points offer numbered options with a recommendation. A spec's
  failing tests are planned as one wave, with mutation testing batched at
  the end.
- The release, secrets, contract, host-parity, version-control, design,
  incident and stewardship postures take the rollback, backup, credential,
  contract, reconcile and diagnosis rules plants had written for
  themselves.
- `skill.library-wiki` now holds the rule for which dependencies get a
  full page when adopting a project, and files a staged research-scout
  draft at close-out. The templates gain setup sharing in a spec's §10,
  rollback per unit, and a record of declined tool candidates.

### Corpora

- Library corpus: 27 new pages and 16 rewritten whole; seed claims the
  review found wrong were corrected against upstream sources. A page for a
  library in preview, or whose next major is a release candidate, says so.
- Tool corpus: 11 new pages and 9 integrated. The seed-data page says a
  demo password lives on disk only, in a file no model reads.
- Skill corpus: new generic and stack-keyed pages. `discardme` is now
  `change-review-report`: the report a reviewer accepts or rejects a
  substantial change from without reading the diff.
- Legal corpus: one new EU regulation page, and four more GDPR provisions
  from the publisher's current text.

### Tools and checks

- `source-index.py` answers `incomplete` with a named record where it used
  to give an empty answer or refuse: `language-not-read` for an input in a
  language it does not read, `reached-over-http` for a test that reaches
  the code only through a URL, and `repository-unnamed` for a work tree
  nested in the plant, while the rest of the moved list is answered.
- `session-metrics.py --all` names on stderr why it found no entry.
- `spec-lint.py` reports a contract slug that only a comment carries as a
  WARN, never as coverage, under a ratchet that may only fall
  (`--comment-only-budget`).
- `graft-audit.py --record` reads any heading that names a graft, in any
  case or position. An entry whose lists name no file fails; a graft that
  merged and kept nothing writes `- none`.
- `agnosticism-lint.py` takes `--forbid-file` (with `!allow` lines),
  `--optional-forbid-file`, `--tracked` and `--terms-only`. A new gate step
  lints every tracked file against the steward's local, gitignored
  `.cypress/forbid.txt`, and prints SKIPPED where that file is absent.
- The gate has 52 steps (`python3 tools/gate-registry.py --summary`).

### Upgrade notes

- **Install Python 3.14 first.** The installer finds `python3.14` and writes
  it into every hook; with no Python at 3.14 or newer on `PATH` it refuses
  before writing. Put a `python3` at 3.14 first on `PATH` for agent
  sessions as well.
- **Graft commits.** The next graft makes a baseline commit of the plant's
  own repository before it writes, then checkpoint commits. It names each
  untracked path and stages none you have not admitted.
- **Keep the stamp tracked.** If the installer prints `.gitignore` lines for
  `.cypress/`, put them in place of a rule that ignores the directory.
- **Decide on backups.** The BACKUPS block and graft list them by date;
  which to keep is your call.
- **Plant agents gain Bash.** A plant-authored agent without a shell is
  given one at the next graft, in a proposal you ratify.
- **Record the routing baseline.** A plant with its own specialists records
  its adversarial baseline at the next graft.
- **Spec coverage may drop.** A plant test that names a contract only in a
  comment no longer covers it; name the contract in the test's code.
- **Steward checkout.** The gate reads the local `.cypress/forbid.txt`; a
  release waits for that step to read PASS in the checkout that holds it.
- New rules in the protocols, method nodes, agents and templates reach an
  existing plant through graft.

### Identifying tokens recast (ADR-0031)

[ADR-0031](docs/decisions/adr-0031-donor-tokens-recast-generically.md)
amends ADR-0011: a token that identifies a project the seed was harvested
from is recast as a generic reference that keeps every fact, an ADR body
included. Under it, these records were edited to remove project names:

- `docs/plans/grill-8.1.0-source-index.md`
- `docs/plans/grill-8.1.2-tool-surfacing.md`
- `docs/decisions/adr-0029-source-index-is-derived-scratch.md`
- `docs/specs/SPEC-0007-source-index.md`
- the 8.1.2 entry of `CHANGELOG.md`
- `.github/RELEASE_NOTES.md`
- `tests/graph-routes.golden.tsv`
- `tests/test-install-adoption.sh`

The original text remains at the prior tags and in the repository's
history. History was not rewritten, no tag was moved, and the published
tags and Releases keep the original text.

### Harvest record

- Harvested: library, tool, skill and legal corpus pages; doctrine and
  template rules across the protocols, method nodes, skills and agents;
  installer and tool fixes for defects plants reported.
- Generalized: every plant name, domain, path, credential, host and port,
  every stack fingerprint and identifying count, every plant version and
  every security fact stripped; documented version facts about a library
  kept with their subject.
- Rejected: plant-specific procedures and configuration; rules the seed
  already owned.

### Seed integrity gate

- G1: PASS
- G2: PASS
- G3: PASS
- G4: PASS
- G5: PASS for every plant the round read but one, which changed by its own
  work during the round
- G6: PASS
- G7: PASS
- G8: PASS
- G9: PASS
- G10: PASS
- G11: PASS
- Version bump: 8.1.2 → 8.2.0

### Known limits

- Two reported defects wait on the owner: routing of task lines written in
  a language other than English, not yet reproduced, and the absolute link
  targets `--symlink` writes, which break when a project moves.
- A hook cannot tell which agent issued a shell command, so the lookup-only
  limit on the new Bash grants is charter text, not a mechanical guard.
