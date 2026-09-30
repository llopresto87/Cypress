---
status: back-written
status_date: 2026-09-30
owner: seed-installer
status_evidence: tests/test-install-placement.sh, tests/test-plant-state.sh, tests/test-install-kernel-modes.sh, tests/test-install-adoption.sh, tests/test-full-install.sh, tests/test-seed-lint.sh, tests/test-graft-tools.sh (all wired into tests/run.sh)
---

# SPEC-0001: install placement

## 0. Metadata

- **Identifier:** SPEC-0001-install-placement
- **Status:** see frontmatter (single home)
- **Sign-offs:** none, and none is owed. This spec is `back-written` — the
  schema's own status for documented existing behaviour (`_schema.md`) — so
  there was no RED for a promotion to land with and no product/architect/tester
  pass has been held. An earlier draft asserted signatures dated to a RED that
  never landed; that was fabricated to satisfy a linter and is recorded here so
  the correction is not silently absorbed. `active` was then used with a long
  argument for why it was honest, which was an argument for `back-written` by
  another name while the right value sat in the schema.

- **Owner:** seed-installer
- **Date:** 2026-09-13
- **Last reviewed:** 2026-09-30
- **Related grill section:** docs/plans/grill-7.15.0-remediation.md §3, §5
- **Related ADRs:** adr-0003-enforcement-layering-honesty, adr-0009-host-support-tiers, adr-0013-harness-memory-is-not-a-home, adr-0014-graft-reconciles-every-graph-engine, adr-0016-stamp-carries-keys-it-does-not-own, adr-0017-pre-growth-pointers-leave-the-kernel, adr-0018-code-fact-freshness-anchor (the last three proposed), adr-0021-seed-only-procedures-stay-home, adr-0022-the-plant-model-map (both proposed)
- **Supersedes:** —
- **Superseded by:** —

## 1. Summary

What `install.sh` is allowed to do to a target directory. The seed's kernel
§3.1 says code without a spec is in remediation mode, and the installer — the
one component that writes into somebody else's repository — had no spec at all.
This contracts the properties that make an install safe to run twice, safe to
run over a customized plant, and safe to audit afterwards: every write is
recoverable, no write escapes the target, an identical re-run changes nothing,
and the record the installer keeps cannot contradict the filesystem. It also
contracts the one write the seed's graft tools make into a plant's placed
files, the reconciliation of the graph engines the installer placed
add-if-missing, and the audit that says whether each engine is current.

## 2. Scope

- **In scope:**
  - every byte `install.sh` writes into `--project-dir`
  - the backup contract and what `--force` does and does not suppress
  - copy vs symlink placement, including the root kernel
  - `.cypress/seed.json` as the plant's persistent record
  - the legal corpus as a whole-or-nothing artifact
  - preflight refusal before any write
  - which hosts `all` installs, and the deprecation notice a frozen host prints
  - the graph-engine reconciliation `tools/graft-graph-engine.py` performs on a
    plant's placed engines (`graph-lint.py`, `spec-lint.py`, `grill-lint.py`),
    and the engine-currency check of `tools/graft-audit.py --engine`
    (adr-0014)
  - the list of re-created nodes written to `.cypress/recreated-nodes.txt`
  - the keys of `.cypress/seed.json` that the installer does not own
    (adr-0016)
  - the placement of `docs/graph/code-anchor.py` (adr-0018)
  - the plant's model map, `docs/graph/models.md`: its placement, the one
    line of each opencode agent projection the installer writes from it, and
    the `--check` that compares those projections with the map (adr-0022)
  - the seed-only files the installer never places, and the tools it does
    place, held against `manifest.json` (adr-0021)
- **Out of scope:**
  - the anchor file `docs/graph/code-anchor.py` writes: SPEC-0003 owns it,
    because the session-start hooks read it and canonize writes it; the
    installer never writes it
  - what the placed files MEAN (the graph schema, the kernel's content)
  - `grow`, `graft` and `harvest`, which are user-sovereign flows over an
    already-installed plant, apart from the engine reconciliation above
  - the seed's own repository layout
  - how Prime Agent reads the model map (overlay prose, brief-enforced), and
    whether a host's model catalog carries a selector the map names

## 3. User-facing behavior

An owner points the installer at a project and names one or more harnesses. The
installer either completes, or refuses before writing anything and says which
path is in the way. Running it again over an unchanged project does nothing and
says nothing. Running it over a project someone has edited replaces the seed's
own files, leaves a timestamped copy of every body it replaced, and names them.
Nothing outside the named project directory is ever modified.
`all` installs the maintained hosts: claude-code, opencode and prime-agent. A
frozen host (codex, github-copilot) still installs when it is named, and says
that it is deprecated. `all --check` still checks the Copilot views of a plant
whose record carries github-copilot, because checking writes nothing, and it
checks the opencode agent projections of a plant whose record carries opencode,
because those carry a `model:` line written from the plant's model map.

## 4. Functional contracts

### Contract: SINGLE_WRITER
- **Given:** any destination inside the target
- **When:** the installer places content there
- **Then:** the write passes through one of four named operations —
  `place_file`, `place_generated`, `place_if_missing`, `place_state`
- **And:** no adapter has a private placement path
- **Except:** 11 writes into the target are authored rather than placed, and are
  recorded here because a contract with unnamed exceptions is a contract that is
  simply false. `record_instruction_migration` (4) moves a symlink off the note
  path, moves a HARD LINK off it for the same reason — `cat >` and `>>` write
  the inode, so a note hardlinked to a file outside the target had the ledger
  appended into that outside file, and `-L` is false for a hardlink — writes the
  note's header, and appends one ledger row per replaced kernel
  — there is no seed-side source file to place, because the body is generated
  from the kernel that was replaced, and none of the four operations expresses
  an append. `place_kernel` (4) backs up the sibling kernel, removes it, lays a
  relative project-local link by hand — `place_file` cannot express a link that
  points inside the target rather than into the seed — and falls back to `cp`
  where the filesystem refused the link. `fill_plant_facts` (1) rewrites
  `docs/graph/index.md` in place through an embedded python heredoc, because the
  plant's facts are merged into a file the plant owns rather than copied over it.
  `ensure_dir` (1) creates a destination directory before a placer writes into
  it — the one write every placer depends on, and a directory rather than
  content, but a write into the target all the same. It was invisible twice
  over: `mkdir` was not a verb the derivation looked for, and `ensure_dir` was
  exempted from the sweep wholesale. `retire_copilot_hook_duplicates` (1) moves
  a `.github/hooks/` file that `.claude/settings.json` now supersedes to a
  timestamped backup beside itself: a removal, which none of the four operations
  expresses, and there is no seed source to place. The Copilot installer already
  skipped those hooks when `settings.json` was present, but that guard ran in
  one direction only — adopting Copilot first and Claude Code second left both
  sets wired, and VS Code reads both, so every hook fired twice.
- **And:** that list is DERIVED from `install.sh` on every run rather than read
  from this page: `seed-lint`'s `check_install_write_sites()` attributes every
  raw write to the function that holds it and compares the set outside the four
  operations against `INSTALL_WRITE_EXCEPTIONS`, **by count as well as by
  shape** — and the four placers are counted too, in `PLACER_WRITES`, rather
  than exempted wholesale. They were exempted wholesale until a reviewer put one
  `case "$dest" in */.github/hooks/*) cat "$src" > "$dest"; return ;; esac`
  inside `place_file` and watched the full gate exit 0 while an install
  destroyed a file outside `--project-dir`. The count above is likewise summed
  from the rows that declare themselves target-side, not written down beside
  them: a row that declares neither side is refused, because "undeclared" used
  to mean "temp, therefore harmless".
- **And:** a new bypass fails because it is absent from that table; a second
  write of an already-excepted shape fails because the count moved; a retired
  one fails because the table is then stale; and the number quoted in the
  sentence above fails if it stops matching the table.
- **And:** the derivation reads shell with regexes, so it is bounded and says
  so. It sees a write behind `if`/`&&`/`;`, a one-line function body, a
  `function name {` definition, and a write performed by an embedded python
  heredoc — the last of which is how `fill_plant_facts` writes, and was
  invisible for as long as the check existed without it. It does NOT see a
  write under a non-python inline interpreter, or under `eval`. Two shapes this
  list used to name — a write inside a command substitution, and a write on the
  right of a pipe — were re-tested during the conformance review and are in fact
  CAUGHT (`_o=$(cp a b)` and `printf x | tee "$dest"` are both found by segment
  splitting), so the list was overstated as well as mislocated: it said these
  residuals were recorded in `tools/gate-registry.py`, and they were not there at
  all. They are recorded in the registry's `seed-lint.py` row now.

### Contract: BACKUP_BEFORE_REPLACE
- **Given:** a destination that exists and differs from what is being placed
- **When:** the installer replaces it
- **Then:** the previous body is recoverable at `<path>.bak-<timestamp>`
- **And:** the two exceptions are `.cypress/seed.json` and
  `.cypress/recreated-nodes.txt`, both written by `place_state`: installer-owned
  derived state, never authored by hand, that would otherwise accrue one backup
  per run

### Contract: FORCE_SUPPRESSES_WARNING_NOT_BACKUP
- **Given:** `--force`
- **When:** a differing destination is replaced
- **Then:** the per-file warning is suppressed and the backup is still made
- **And:** no flag exists that replaces a file without a recovery copy

### Contract: SYMLINK_IS_REPLACED_NOT_FOLLOWED
- **Given:** a destination that is a symlink to a file outside the target
- **When:** the installer places content at that destination
- **Then:** the link object is moved aside or replaced
- **And:** the referent outside the target is unchanged

### Contract: IDENTICAL_RERUN_IS_INERT
- **Given:** a plant nobody has modified since the last install
- **When:** the same install command runs again
- **Then:** no file is rewritten and no `.bak-*` is created

### Contract: EVERY_BACKUP_IS_CLASSIFIABLE
- **Given:** any backup the installer produced
- **When:** `tools/graft-audit.py` runs over the plant
- **Then:** the backup classifies as identical, delta, customized, generated, or
  a named exclusion — never `UNMAPPED`
- **And:** an unclassifiable backup makes the audit exit non-zero rather than
  report "clean"

### Contract: SYMLINK_MODE_IS_UNIFORM
- **Given:** `--symlink`
- **When:** the install completes
- **Then:** every placed file is a symlink, except generated content and
  add-if-missing plant-owned files, which have no seed original to point at
- **And:** the root kernel is a link, so a seed kernel change reaches the plant
  without reinstalling

### Contract: COPY_MODE_ISOLATES
- **Given:** `--copy` (the default)
- **When:** the seed's kernel changes afterwards
- **Then:** the installed plant is unaffected until it is reinstalled

### Contract: ONE_KERNEL_BODY
- **Given:** a plant running more than one harness
- **When:** the install completes, in any adapter order
- **Then:** exactly one of `CLAUDE.md` / `AGENTS.md` is a real file and the other
  is a project-local relative symlink to it
- **And:** both resolve to byte-identical content

### Contract: DECISIONS_SURVIVE_SILENCE
- **Given:** a recorded owner decision in `.cypress/seed.json`
- **When:** a later install passes no flag for it
- **Then:** the recorded value is preserved
- **And:** only `undecided` is ever overwritten by silence

### Contract: ADAPTERS_ACCUMULATE
- **Given:** a plant already carrying one or more adapters
- **When:** another adapter is installed
- **Then:** the recorded adapter set is the union, and `agent_projections` is
  derived from it rather than maintained separately

### Contract: RECORD_AGREES_WITH_DISK
- **Note (corrected):** the inheritance re-check covered only the `yes`
  direction, so the record could say `legal_corpus: no` over statutes on disk —
  two ordinary commands, exit 0, no warning — while `agent.legal` answers from
  the corpus rather than from the stamp. The `no` direction now refuses the same
  way the explicit flag always did. Separately, the closing banner gated on flag
  SILENCE rather than on the resolved value, so a plant recording `no` was told
  its own file said `undecided`.
- **Given:** an installed legal corpus
- **When:** an install would record `legal_corpus: no`
- **Then:** the install is refused, naming both ways out
- **And:** neither the corpus nor the record is changed by the refusal

### Contract: CORPUS_IS_WHOLE_OR_ABSENT
- **Given:** `--legal-corpus yes`
- **When:** placement completes
- **Then:** the plant carries **no fewer than** every page the seed ships,
  counting pages and not backups. A shortfall is refused; a surplus is the
  plant's own ingest, is named in the log, and is not a reason to refuse.
- **Note (corrected):** this `Then` read "the number of corpus pages in the
  plant EQUALS the number in the seed", and equality is the wrong test. A plant
  that did what the installer's own notice tells it to do — run a
  research-scout ingest and land its national statute under
  `docs/graph/legal/corpus/` — got `legal corpus placed partially (17 of 16
  pages)` and could never install again. The code was corrected to `-lt` first
  and this sentence was left asserting the falsified version, four lines below
  the note recording the correction; the cited test asserted `-eq` as well.

### Contract: PREFLIGHT_REFUSES_BEFORE_WRITING
- **Given:** a target where a directory the preflight ENUMERATES already exists
  as a regular file, is not writable, or is a symlink leaving the target
- **When:** the installer runs
- **Then:** it exits non-zero naming the offending path, and the target is
  unchanged
- **And:** the failure is the tool's own message, not a raw shell error
- **Except:** a directory the preflight does not enumerate. The `Given` above
  read "a needed directory" with no qualifier, and that was false by 239 paths:
  a regular file at `.claude/skills/library-wiki` — a per-skill leaf the
  preflight does not reach — refuses only when `ensure_dir` meets it, after 239
  paths are already written, and a variant of the same case replaces the
  project's own `CLAUDE.md` and THEN refuses. `install.sh`'s `ensure_dir` header comment documents this
  honestly as "the preflight is the early warning, and this is the floor
  underneath it"; the contract asserted the opposite. What the preflight DOES
  enumerate is: `adapter_dirs()` for every selected tool, every directory that
  already exists beneath the trees the installer writes
  (`PREFLIGHT_SCOPED_TO_WRITTEN_TREES`), and every existing symlink beneath those
  trees. The last two are walked rather than listed, so they do not depend on
  anyone remembering to add a path.

### Contract: PREFLIGHT_SCOPED_TO_WRITTEN_TREES
- **Given:** a target that holds unwritable directories, or a directory symlink
  leaving the target, in a tree the installer never writes: `node_modules/`,
  `.next/`, a database volume, a nested checkout, `test-results/`. Docker builds
  and test runs leave such trees, often owned by root.
- **When:** the installer runs
- **Then:** it installs, and it does not open, change or refuse over those trees
- **And:** the deep walks for an unwritable directory and for an escaping
  symlink cover only the trees a run writes: `docs/graph`, `.cypress`, each
  selected adapter's own top directory, and the four `.github` subdirectories
  the Copilot adapter writes. The roots come from `adapter_dirs()`, so a new
  adapter is covered by its own entry.
- **Except:** none inside a written tree. A read-only directory or an escaping
  symlink under `docs/graph`, `.cypress` or an adapter directory still refuses
  before the first byte (`PREFLIGHT_REFUSES_BEFORE_WRITING`,
  `SYMLINK_IS_REPLACED_NOT_FOLLOWED`).

### Contract: ALL_EXCLUDES_LEGACY_HOSTS
- **Given:** an empty target
- **When:** `install.sh all` runs
- **Then:** `.claude/`, `.opencode/` and `.prime/agent/` exist, and `.codex/` and
  `.github/` do not
- **And:** the stamp's `tools` is exactly `claude-code opencode prime-agent`

### Contract: LEGACY_INSTALL_PRINTS_DEPRECATED
- **Given:** an empty target
- **When:** `install.sh codex` or `install.sh github-copilot` runs
- **Then:** stderr carries exactly one `DEPRECATED` line, naming that tool and
  ADR-0009
- **And:** `install.sh opencode` prints no such line

### Contract: LEGACY_INSTALL_STILL_SUCCEEDS
- **Given:** an empty target
- **When:** a frozen host is named
- **Then:** the install exits 0 and places that host's destinations as 7.26.0 did
- **And:** `codex --print-config` keeps the notice off stdout, which carries
  config a user pastes, and still prints it on stderr

### Contract: ALL_NAMES_SKIPPED_FROZEN_HOSTS
- **Given:** a plant whose stamp records `codex`
- **When:** `install.sh all` runs
- **Then:** stderr names `codex` as not refreshed, together with the command that
  refreshes it, `install.sh all codex`
- **And:** `.codex/` is byte-identical before and after, and the stamp still
  lists `codex` (ADAPTERS_ACCUMULATE)

### Contract: CHECK_WITHOUT_COPILOT_SAYS_SO
- **Given:** a target whose record carries neither github-copilot nor
  opencode, the two hosts whose views `--check` can compare
- **When:** `install.sh all --check` runs
- **Then:** it exits 0 and prints that no generated views are in scope
- **And:** silence is the failure, because a CI job reading only the exit code
  would take it for "in sync"

### Contract: ALL_CHECK_INCLUDES_RECORDED_COPILOT
- **Given:** a plant whose `.cypress/seed.json` records github-copilot
- **When:** `install.sh all --check` runs
- **Then:** the Copilot views are checked as `install.sh github-copilot --check`
  checks them: in sync, it exits 0 and reports them up to date; drifted, it
  exits non-zero and names them STALE
- **And:** the not-refreshed warning of FROZEN_PROJECTION_LEFT_STALE does not
  fire for github-copilot, which this run checks. The DEPRECATED notice does
  fire, once, because the run acts on a frozen host, the same as a `--check`
  that names it

### Contract: HOST_TIERS_AGREE
- **Given:** the tier arrays in `install.sh` (the one home of the assignment)
- **When:** `seed-lint` runs
- **Then:** it fails, naming `install.sh`, when a host sits in two tiers, or
  when `all` expands to anything but the first-class and supported hosts
- **And:** it fails, naming `install.sh`, when the three arrays together are not
  exactly the labels of the adapter dispatch `case "$tool"` block, whatever
  shape an arm's command takes, or when a label there is not a bare tool name
- **And:** it fails, naming `install.sh`, when the argument parser's
  `case "$1"` arms that append to `TOOLS` accept anything but the three
  arrays' hosts plus `all`
- **And:** it fails, naming the suite, when the `EVERY_HOST` literal in
  `tests/test-full-install.sh`, `tests/test-install-placement.sh` or
  `tests/test-unified-graph-install.sh` names a different set of tools than
  the dispatch installs
- **And:** the unmutated tree passes

### Contract: SESSION_RECORD_FORM_IS_PLACED
- **Given:** a fresh target directory
- **When:** `install.sh claude-code --project-dir <target>` runs
- **Then:** `docs/graph/plans/sessions/_session-record.template.md` exists
  and is byte-identical to the seed's
  `templates/docs/plans/sessions/_session-record.template.md`, placed by
  `place_docs_skeleton`'s existing `templates/docs/**` walk with
  `place_if_missing`, so `SINGLE_WRITER`'s census is unchanged
- **And:** after the plant writes its own record in
  `docs/graph/plans/sessions/` and edits the placed form, `install.sh all
  --project-dir <target>` leaves both files byte-identical and writes no
  backup beside either

### Contract: ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE
- **Given:** a plant engine file and the seed's engine of the same name
- **When:** `tools/graft-graph-engine.py <plant-file> <seed-file>` runs with no
  `--preserve`
- **Then:** it preserves the config that engine carries: `ROOT_ID`, `KINDS`
  and `KIND_PREFIX` for `graph-lint.py`; `TEST_GLOBS` for `spec-lint.py`;
  nothing for `grill-lint.py`; and exits 0, having adopted the seed body with
  a `.bak-<ts>` of the plant file, or reporting it already current or
  KEEP-PLANT
- **And:** a plant file with any other name takes the `graph-lint.py` set
- **And:** an explicit `--preserve` wins over the per-engine set

### Contract: ENGINE_AUDIT_CHECKS_EVERY_PAIR
- **Given:** `tools/graft-audit.py <plant> <seed>` with `--engine
  <plant-file>:<seed-file>` given more than once
- **When:** it runs
- **Then:** it prints one engine-currency line per pair, each naming its plant
  file
- **And:** a malformed or unreadable pair, in any position, makes it exit
  non-zero, because a check that did not run is not reported as run

### Contract: EXISTING_PLANT_RECEIVES_CURRENT_ENGINES
- **Given:** an installed plant whose `docs/graph/grill-lint.py` is an older
  engine body
- **When:** `install.sh` re-runs
- **Then:** `docs/graph/grill-lint.py` is unchanged: the engines stay
  plant-owned
- **And:** when `tools/graft-graph-engine.py` then runs, with no
  `--preserve`, over each of the three engines, every run exits 0,
  `docs/graph/grill-lint.py` is byte-identical to the seed's, one backup holds
  the older body, and `python3 docs/graph/grill-lint.py --waves` prints a line
  starting `waves:`
- **And:** `tools/graft-audit.py` with the three `--engine` pairs reports
  every engine current

### Contract: PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION
- **Given:** a target whose `CLAUDE.md` (or `AGENTS.md`) is byte-identical to
  `core/AGENTS.md` at an earlier commit of the seed checkout the installer runs
  from, and differs from the current `core/AGENTS.md`
- **When:** `install.sh claude-code --project-dir <target>` runs
- **Then:** the kernel is replaced with a backup, as `BACKUP_BEFORE_REPLACE`
  requires, and `docs/graph/plans/adopted-instructions.md` gains no row for
  that backup
- **And:** stderr carries no `OVERWRITTEN` line for it; the log names the
  replacement as a fast-forward from an earlier seed kernel
- **And:** a later run's orphan sweep files no row for that backup either
- **And:** a kernel body that matches no seed kernel in that history is filed
  exactly as today

### Contract: RECREATED_LIST_IS_COMPLETE
- **Given:** an installed plant whose `.cypress/seed.json` predates the run and
  from which twelve seed-owned graph nodes were deleted
- **When:** `install.sh claude-code --project-dir <target>` runs again
- **Then:** `.cypress/recreated-nodes.txt` lists all twelve paths, one per line,
  sorted and unique, under the header line §6 gives
- **And:** the console notice still prints at most ten paths, and it names the
  file that holds the whole list
- **And:** a later run that re-creates nothing rewrites the file with the header
  line alone, so the file always describes the run that last wrote the stamp

### Contract: UNKNOWN_STAMP_KEYS_SURVIVE
- **Given:** a `.cypress/seed.json` that holds the installer's own keys plus two
  keys the installer does not own, one a string and one an object
- **When:** `install.sh all --project-dir <target>` runs with no flag
- **Then:** both keys are in the new stamp with JSON-equal values, in their
  original order, after the installer's own keys
- **And:** the installer's own keys follow their existing rules
  (`DECISIONS_SURVIVE_SILENCE`, `ADAPTERS_ACCUMULATE`)

### Contract: PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX
- **Given:** a fresh target directory
- **When:** `install.sh claude-code --project-dir <target>` runs
- **Then:** `docs/graph/index.md` holds one pre-growth block, delimited as §6
  gives, that names `EXPERT_SEED_INSTALL_PROMPT.md` and `protocol.initialize`
- **And:** the placed kernel, `CLAUDE.md`, names neither
  `EXPERT_SEED_INSTALL_PROMPT.md` nor `protocol.initialize`
- **And:** a re-install over a plant whose `index.md` has no such block leaves
  that `index.md` byte-identical, because the index is plant-owned

### Contract: CODE_ANCHOR_TOOL_IS_PLACED
- **Given:** a fresh target directory
- **When:** `install.sh all --project-dir <target>` runs
- **Then:** `docs/graph/code-anchor.py` exists and is byte-identical to the
  seed's `tools/code-anchor.py`
- **And:** no `.cypress/anchor.json` exists, because only canonize records an
  anchor
- **And:** a re-install over an older copy of the tool replaces it with a
  backup, as it does `docs/graph/status-register.py`

### Contract: MODEL_MAP_TEMPLATE_IS_PLACED
- **Given:** a fresh target directory
- **When:** `install.sh claude-code --project-dir <target>` runs
- **Then:** `docs/graph/models.md` exists and is byte-identical to the seed's
  `templates/docs/models.md`, placed by `place_docs_skeleton`'s existing
  `templates/docs/**` walk with `place_if_missing`, so `SINGLE_WRITER`'s
  census is unchanged
- **And:** after the plant edits the placed map, `install.sh all
  --project-dir <target>` leaves it byte-identical and writes no backup
  beside it

### Contract: OPENCODE_MODEL_FROM_MAP
- **Given:** a plant whose `docs/graph/models.md` fills the opencode cell of
  the `authoring | high` row with `` `provider-a/model-x` `` and of the
  `investigation | medium` row with `` `provider-b/model-y` ``, and whose
  graph holds an agent with `model: opus` and `effort: high` and one with
  `model: sonnet` and `effort: medium`
- **When:** `install.sh opencode --project-dir <target>` runs
- **Then:** each of the two agents' `.opencode/agents/<name>.md` equals its
  graph home `docs/graph/agents/<name>.md` with the `model:` line replaced by
  `model: provider-a/model-x` and `model: provider-b/model-y` respectively,
  and with no other byte changed
- **And:** the projection is written through `place_generated`, so it is a
  real file under `--symlink` as well, and `SINGLE_WRITER`'s exception count
  is unchanged
- **And:** the stamp's `agent_projections` entry for opencode records
  `"verbatim": false`
- **And:** a plant agent with `model: haiku` gets the opencode cell of the
  `investigation | low` row, whatever its `effort:` says (§6)

### Contract: OPENCODE_NO_MAP_ROW_NO_MODEL_LINE
- **Given:** a fresh target, so `docs/graph/models.md` is the unfilled
  template
- **When:** `install.sh opencode --project-dir <target>` runs
- **Then:** it exits 0, and each `.opencode/agents/<name>.md` equals its graph
  home with the `model:` line removed and no other byte changed
- **And:** the same holds, in a map whose other rows are filled, for an agent
  whose class and effort have no row, for one whose row's opencode cell is
  `-`, and for a plant agent with `model: inherit`, whatever the map says
- **And:** stdout carries one line that names `docs/graph/models.md` and the
  number of agents projected with no `model:` line, so an agent that runs on
  its caller's model is never silent

### Contract: OPENCODE_MAP_UNREADABLE_FAILS_CLOSED
- **Given:** an installed opencode plant whose `docs/graph/models.md` breaks
  the §6 map grammar (for example, a row whose class is `premium`)
- **When:** `install.sh opencode --project-dir <target>` runs
- **Then:** it exits non-zero, and stderr names `docs/graph/models.md` and the
  offending line
- **And:** every `.opencode/agents/*.md` is byte-identical to its state
  before the run, and no backup is made beside any of them

### Contract: OPENCODE_CHECK_DETECTS_DRIFT
- **Given:** an opencode plant, its record carrying opencode, installed with a
  map that fills the opencode cell of the `authoring | high` row
- **When:** `install.sh opencode --check --project-dir <target>` runs
- **Then:** after a hand edit to one `.opencode/agents/<name>.md`, it exits
  non-zero and names that projection as stale
- **And:** after an edit of the map's filled cell with no re-run, which
  changes only `model:` lines, it exits non-zero and names each projection
  whose `model:` line the edit changes
- **And:** the expected set is rendered from the plant's `docs/graph/agents/`
  and `docs/graph/models.md` by the §6 projection rule and compared with the
  plant's `.opencode/agents/`, backups excluded, so a projection that is
  missing, or that has no graph home, is stale too
- **And:** in sync, it exits 0 and says the opencode projections are up to
  date
- **And:** every run leaves the plant byte-identical: no projection, backup or
  stamp is written
- **And:** `install.sh all --check` checks the same projections, because
  `all` names opencode and the record carries it

### Contract: SEED_ONLY_FILES_NEVER_PLACED
- **Given:** `SEED_ONLY` in `tests/seed-lint.py`, which names
  `tools/prepare-release.py` and `docs/skills/seed-release.md` (adr-0021)
- **When:** `seed-lint` runs
- **Then:** it fails, naming the path, when a `SEED_ONLY` path is missing from
  the seed or `manifest.json` names it
- **And:** it fails, naming `install.sh`, when the installer names a
  `SEED_ONLY` path or sources any file under `$SEED_ROOT/docs`
- **And:** it fails, naming `manifest.json`, when the keys of its `tools` map
  differ from the set of `$SEED_ROOT/tools/*` and `$SEED_ROOT/tests/*` files
  `install.sh` places

## 5. Non-functional requirements

- **Compatibility:** bash and `python3` only; no third-party imports. The
  binding shell floor is bash, not the POSIX subset: `install.sh:1` declares
  `#!/usr/bin/env bash`, `:69` uses `set -euo pipefail` whose `pipefail` POSIX's
  `set` does not define, and every shell file in this tree declares a bash
  shebang. The in-tree constraint that is recorded is the bash 3.2 floor
  (`install.sh:1824`, `:2192`). The two floors are different and a grown
  plant's graph owns the distinction at `docs/graph/best-practices/bash.md`
  §"Two floors, not one"; it is not restated here. (This line claimed a POSIX
  shell floor until 2026-09-16 — see §12.)
  Placement is exercised on Linux and macOS in CI, because symlink semantics are
  where the platforms differ.
- **Reliability:** generation completes before replacement, so a failed
  generation cannot leave a partial destination.
- **Security:** an install may not modify any path outside `--project-dir`.

## 6. Data shapes

```yaml
# .cypress/seed.json — the plant's persistent record
seed:                 { type: string, const: "cypress" }
version:              { type: string }            # seed version now installed
installed_at:         { type: string, format: rfc3339 }
installed_from:       { type: string, optional: true }
tools:                { type: string }            # space-joined adapter list, accumulating
legal_corpus:         { enum: [yes, no, undecided] }
legal_jurisdiction:   { type: string }            # two-letter code, or "undecided"
agent_projections:    { type: array, derived_from: tools }
```

Beyond the keys above, the stamp has one rule: any key the installer does not
own is carried forward unchanged.

```yaml
# .cypress/seed.json, additions to the shape above
additional_keys:      { carried: unchanged, order: kept, after: installer keys }
```

```text
# .cypress/recreated-nodes.txt: written by every run that writes the stamp
# install.sh <version> <UTC rfc3339>: seed-owned graph nodes re-created by this run
docs/graph/protocols/grill.md
docs/graph/skills/humanizer/SKILL.md
```

The pre-growth block in the placeholder `docs/graph/index.md` opens with the
line `<!-- pre-growth: grow removes this block -->` and closes with the line
`<!-- /pre-growth -->`. `protocol.grow` removes it in the phase that sets
`grown: true`.

The stamp's `agent_projections` entry for opencode reads
`{"tool": "opencode", "path": ".opencode/agents/{name}.md", "verbatim": false}`
(adr-0022); the other hosts' entries are unchanged.

The model map, `docs/graph/models.md` (adr-0022), is placed from
`templates/docs/models.md` when missing and is plant-owned from then on. The
opencode projection reads one table from it:

```text
# the first table under the `## Map` heading
header:   | Class | Effort | Prime Agent | opencode |          exact
class:    authoring | investigation                          closed set
effort:   low | medium | high                                closed set
rows:     at most one per (class, effort); a missing pair reads as unfilled
cell:     `<provider>/<model>`   one inline-code span, at least one "/", no
                                 whitespace, no "<" or ">"           filled
          `<...>` or <...>       the template's placeholder          unfilled
          -                      inherit the caller's model          unfilled
token:    model: opus   -> authoring, the agent's effort
          model: sonnet -> investigation, the agent's effort
          model: haiku  -> investigation, low (the agent's effort is not read)
          model: inherit -> no row: the projection carries no model line
```

The opencode projection of a graph agent follows from its frontmatter:

| The agent's `model:` and `effort:` | The projected `model:` line |
|---|---|
| `opus`, `sonnet` or `haiku`, and the map's cell for its (class, effort) is filled | `model: <cell>`, in place of the token |
| `opus`, `sonnet` or `haiku`, and the cell is unfilled, the row is missing, the `effort:` of an `opus` or `sonnet` agent is missing, or the map is absent | none |
| `inherit`, or no `model:` key | none |
| any other `model:` value | copied unchanged |

A map is absent when the plant renamed it by hand to
`docs/graph/models.unfilled.md`, a marker `place_docs_skeleton` honours by
leaving `docs/graph/models.md` unplaced; `graft-audit.py --rename` leaves the
map in place (ADR-0022, S4). The Prime
Agent column is read by the Prime Agent overlay, and the installer does not
read it.

`--check` renders the same rule into a scratch directory under the run's stage
and compares it with `.opencode/agents/`, excluding `*.bak-*`. The opencode
projections are in its scope when the run names opencode, directly or through
`all`, and the stamp's `tools` carries opencode; the Copilot views keep their
own scope rule (ALL_CHECK_INCLUDES_RECORDED_COPILOT). With neither in scope,
the run says that no generated views are in scope and exits 0.

## 7. Failure modes

### Failure: DESTINATION_PATH_OCCUPIED
- **Trigger:** a needed directory exists as a regular file
- **Response:** non-zero exit naming every offending path
- **Side effects:** none for an ENUMERATED path — the refusal precedes the
  first write. For a path the preflight does not reach (a per-skill leaf under
  `.claude/skills/`), `ensure_dir` refuses late and the writes already made
  stand; see PREFLIGHT_REFUSES_BEFORE_WRITING's `Except`.
- **Recovery:** move or remove the file and re-run

### Failure: TARGET_NOT_WRITABLE
- **Trigger:** the target directory denies writes
- **Response:** non-zero exit naming the path
- **Side effects:** none
- **Recovery:** fix permissions and re-run

### Failure: CONTRADICTORY_CORPUS_TRANSITION
- **Trigger:** `--legal-corpus no` while corpus pages are installed
- **Response:** non-zero exit naming the page count and both remedies
- **Side effects:** none; the installer never deletes a corpus
- **Recovery:** record `yes`, or remove the corpus deliberately and then `no`

### Failure: PARTIAL_CORPUS
- **Trigger:** placed page count does not equal the seed's
- **Response:** `die` — a subset makes a missing instrument indistinguishable
  from one that does not apply
- **Recovery:** re-run; investigate placement if it recurs

### Failure: FROZEN_PROJECTION_LEFT_STALE
- **Trigger:** the stamp records a frozen host and `install.sh all` runs
  without acting on it (a github-copilot that `all --check` checks is acted on;
  see ALL_CHECK_INCLUDES_RECORDED_COPILOT)
- **Response:** one `WARNING` line per such host on stderr: its files were not
  refreshed, and `install.sh all <host>` refreshes them
- **Side effects:** none; the frozen host's tree is left exactly as it was
- **Recovery:** re-run with the host named

### Failure: ENGINE_LEFT_STALE_BY_GRAFT
- **Trigger:** a graft reconciles fewer than the three engines, or the engine
  tool refuses one and the refusal is not acted on
- **Response:** `graft.gate.engine`, run with the three pairs, prints a `graph
  engine STALE` line naming the stale engine (`detective`: the line does not
  gate the exit code)
- **Side effects:** the plant keeps its older engine; for `grill-lint.py`,
  `--waves` is missing
- **Recovery:** run `tools/graft-graph-engine.py` over the named engine, or
  record a superset as KEEP-PLANT

### Failure: SEED_HISTORY_UNAVAILABLE
- **Contracts:** PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION
- **Trigger:** the seed root is not a Git work tree, or `git` is not on `PATH`
- **Response:** the kernel is compared with the current `core/AGENTS.md` only,
  as before 7.32.0, and the log says so in one line
- **Side effects:** a pristine older kernel body is filed for migration: work
  for `docs-librarian` that turns out to be empty, never a lost instruction
- **Recovery:** none needed; the librarian strikes the row

### Failure: STAMP_NOT_AN_OBJECT
- **Contracts:** UNKNOWN_STAMP_KEYS_SURVIVE
- **Trigger:** `.cypress/seed.json` parses as JSON but its top level is not an
  object (an array, a string, a number, `true`, `false` or `null`)
- **Response:** the installer moves it aside to a `.bak-<ts>` sibling, writes a
  stamp from its own keys as before 7.32.0, and prints one warning that names
  the backup and says the keys it does not own could not be carried
- **Side effects:** those keys are in the backup only
- **Recovery:** the owner copies them back by hand

### Failure: MODEL_MAP_UNREADABLE
- **Contracts:** OPENCODE_MAP_UNREADABLE_FAILS_CLOSED, OPENCODE_CHECK_DETECTS_DRIFT
- **Trigger:** `docs/graph/models.md` exists and is not UTF-8, or its
  `## Map` table is missing, has a header other than §6's or no separator row
  under it, holds a row without four cells or a class or an effort outside §6's
  closed sets, repeats a (class, effort) pair, or has an opencode cell that is
  none of §6's cell forms; or `docs/graph/models.md` is a symlink leaving the
  target, which is refused as `docs/graph/index.md`'s is
  (SYMLINK_IS_REPLACED_NOT_FOLLOWED), naming the link
- **Response:** `die` naming the file and the offending line, before the
  first opencode agent is projected; under `--check`, the same exit and message
  before any comparison, so an unreadable map is never reported in sync
- **Side effects:** none under `--check`. Otherwise the writes the run made
  before the opencode adapter stand (the kernel, `docs/graph/`, an earlier
  adapter's tree); the opencode projections are unchanged; the stamp is not
  rewritten, because `write_seed_stamp` runs after every adapter
- **Recovery:** fix the map and re-run

### Failure: OPENCODE_SELECTOR_UNRESOLVED
- **Contracts:** OPENCODE_MODEL_FROM_MAP
- **Trigger:** a filled opencode cell names a `provider/model` the host's
  catalog does not carry
- **Response:** none from the installer, which has no access to the host's
  catalog and writes the cell as given. What opencode does when it spawns that
  agent: not recorded
- **Side effects:** that agent may fail to spawn on opencode
- **Recovery:** fix the row and re-run `install.sh opencode`

## 8. Examples

```
# inert re-run
$ install.sh all --project-dir /p && install.sh all --project-dir /p
$ find /p -name '*.bak-*' | wc -l
0

# a destination symlinked outside the target
$ ln -s /elsewhere/secret /p/.claude/route-hook.py
$ install.sh claude-code --project-dir /p
$ cat /elsewhere/secret        # unchanged; the LINK was replaced

# refused contradiction
$ install.sh claude-code --legal-corpus no --project-dir /p
ERROR: refusing --legal-corpus no: 16 corpus page(s) are installed at ...
$ echo $?
1
```

## 9. Acceptance criteria

- [x] AC-1: every destination is recoverable — maps to BACKUP_BEFORE_REPLACE,
      SINGLE_WRITER
- [x] AC-2: no install modifies a file outside the target — maps to
      SYMLINK_IS_REPLACED_NOT_FOLLOWED
- [x] AC-3: an unchanged plant re-installs to zero churn — maps to
      IDENTICAL_RERUN_IS_INERT
- [x] AC-4: every backup is classifiable by the audit — maps to
      EVERY_BACKUP_IS_CLASSIFIABLE
- [x] AC-5: one kernel body regardless of adapter order — maps to
      ONE_KERNEL_BODY, COPY_MODE_ISOLATES, SYMLINK_MODE_IS_UNIFORM
- [x] AC-6: owner decisions survive unrelated installs — maps to
      DECISIONS_SURVIVE_SILENCE, ADAPTERS_ACCUMULATE
- [x] AC-7: the record cannot contradict the disk — maps to
      RECORD_AGREES_WITH_DISK, CORPUS_IS_WHOLE_OR_ABSENT
- [x] AC-8: a bad target is refused before any write — maps to
      PREFLIGHT_REFUSES_BEFORE_WRITING
- [ ] AC-9: an upgrade over a pristine earlier seed kernel files no migration
      work, and a kernel with a plant line is still filed — maps to
      PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION
- [ ] AC-10: the graft's re-created-nodes evidence is complete — maps to
      RECREATED_LIST_IS_COMPLETE
- [ ] AC-11: a stamp annotation survives every install — maps to
      UNKNOWN_STAMP_KEYS_SURVIVE
- [ ] AC-12: a grown plant's kernel carries no pre-growth pointer — maps to
      PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX
- [ ] AC-13: every plant has the anchor tool the hooks call, and no install
      writes an anchor — maps to CODE_ANCHOR_TOOL_IS_PLACED
- [ ] AC-14: every plant receives an unfilled model map, which it then owns;
      maps to MODEL_MAP_TEMPLATE_IS_PLACED
- [ ] AC-15: an opencode agent carries the model the plant's map names, or no
      model line where the map names none; maps to OPENCODE_MODEL_FROM_MAP,
      OPENCODE_NO_MAP_ROW_NO_MODEL_LINE
- [ ] AC-16: a map the installer cannot read stops the opencode projection and
      leaves it as it was; maps to OPENCODE_MAP_UNREADABLE_FAILS_CLOSED
- [ ] AC-17: a seed-only file never reaches a plant; maps to
      SEED_ONLY_FILES_NEVER_PLACED
- [ ] AC-18: a drifted opencode projection, its `model:` line included, is
      reported by `--check`, which writes nothing; maps to
      OPENCODE_CHECK_DETECTS_DRIFT

## 10. Test mapping

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| SINGLE_WRITER | M7 sweep over the discovered destination set | tests/test-install-placement.sh | integration | green |
| SINGLE_WRITER | check_install_write_sites — the exception set is exhaustive, by count as well as by shape | tests/seed-lint.py | unit | green |
| BACKUP_BEFORE_REPLACE | M7 sweep | tests/test-install-placement.sh | integration | green |
| SYMLINK_IS_REPLACED_NOT_FOLLOWED | M2 attack over every destination | tests/test-install-placement.sh | integration | green |
| IDENTICAL_RERUN_IS_INERT | M3 churn check (names the churned files) | tests/test-install-placement.sh | integration | green |
| SYMLINK_MODE_IS_UNIFORM | M9 link-uniformity check, inside case_symchurn | tests/test-install-placement.sh | integration | green |
| EVERY_BACKUP_IS_CLASSIFIABLE | M8 audit-totality check: every backup of a real install classifies; the UNMAPPED exit is held by X390's second arm | tests/test-install-placement.sh | integration | green |
| FORCE_SUPPRESSES_WARNING_NOT_BACKUP | M4: --force keeps every backup, and without it the backup is announced | tests/test-install-placement.sh | integration | green |
| ONE_KERNEL_BODY | K1/K4/K5 cases | tests/test-install-kernel-modes.sh | integration | green |
| COPY_MODE_ISOLATES | K2 case | tests/test-install-kernel-modes.sh | integration | green |
| SYMLINK_MODE_IS_UNIFORM | K3 case | tests/test-install-kernel-modes.sh | integration | green |
| DECISIONS_SURVIVE_SILENCE | S1 case | tests/test-plant-state.sh | integration | green |
| ADAPTERS_ACCUMULATE | S2/S5 cases, both orders | tests/test-plant-state.sh | integration | green |
| RECORD_AGREES_WITH_DISK | S6 refusal case | tests/test-plant-state.sh | integration | green |
| CORPUS_IS_WHOLE_OR_ABSENT | S6 whole-corpus case | tests/test-plant-state.sh | integration | green |
| CONTRADICTORY_CORPUS_TRANSITION | S6 refusal leaves disk and record untouched | tests/test-plant-state.sh | integration | green |
| PREFLIGHT_REFUSES_BEFORE_WRITING | D1 inside case_block_declared and case_block_readonly: the preflight refuses before any write (`.claude`-as-a-file, read-only target) | tests/test-install-adoption.sh | integration | green |
| PREFLIGHT_SCOPED_TO_WRITTEN_TREES | D6 case_unrelated_trees: unwritable trees and an escaping directory link outside the written set do not refuse the install, and are unchanged afterwards | tests/test-install-adoption.sh | integration | green |
| SYMLINK_IS_REPLACED_NOT_FOLLOWED | M10 (6) a symlinked DIRECTORY leaving the target is refused, at two paths (an adapter directory and a `docs/graph/` subtree), M10 (7) one staying inside still works — §5's Security NFR and §9 AC-2 rest on this | tests/test-install-placement.sh | integration | green |
| DESTINATION_PATH_OCCUPIED | D1 inside case_block_declared: destination occupied by a non-directory | tests/test-install-adoption.sh | integration | green |
| TARGET_NOT_WRITABLE | D1 inside case_block_readonly: target directory not writable | tests/test-install-adoption.sh | integration | green |
| PARTIAL_CORPUS | (no behavioural test — see §11) | — | — | pending |
| ALL_EXCLUDES_LEGACY_HOSTS | E1 caseALL_EXCLUDES_LEGACY_HOSTS: `all` places three hosts, and the stamp lists exactly those | tests/test-full-install.sh | integration | green |
| LEGACY_INSTALL_PRINTS_DEPRECATED | E2 case_codex, case_github_copilot: one DEPRECATED line naming the tool and ADR-0009; that a maintained host prints none is held by E1 caseALL_EXCLUDES_LEGACY_HOSTS | tests/test-full-install.sh | integration | green |
| LEGACY_INSTALL_STILL_SUCCEEDS | E3 case_codex, case_github_copilot: exit 0, two destinations each, `--print-config` stdout clean | tests/test-full-install.sh | integration | green |
| ALL_NAMES_SKIPPED_FROZEN_HOSTS | S8 caseALL_NAMES_SKIPPED_FROZEN_HOSTS: the skip and its refresh command named, `.codex/` byte-identical, stamp keeps codex | tests/test-plant-state.sh | integration | green |
| FROZEN_PROJECTION_LEFT_STALE | S8 caseALL_NAMES_SKIPPED_FROZEN_HOSTS (the same case holds the warning and the untouched tree) | tests/test-plant-state.sh | integration | green |
| CHECK_WITHOUT_COPILOT_SAYS_SO | D3 caseCHECK_WITHOUT_COPILOT_SAYS_SO: `all --check` exits 0 and says no generated views are in scope, on a target with no record and on a plant whose record carries neither github-copilot nor opencode (`install.sh claude-code codex`) | tests/test-install-adoption.sh | integration | green |
| ALL_CHECK_INCLUDES_RECORDED_COPILOT | D4 caseALL_CHECK_INCLUDES_RECORDED_COPILOT: a Copilot-recording plant is checked by `all --check`, in sync exits 0 with "up to date", drifted exits non-zero with STALE, no not-refreshed warning. The DEPRECATED notice of this run is held by E2 (LEGACY_INSTALL_PRINTS_DEPRECATED) | tests/test-install-adoption.sh | integration | green |
| HOST_TIERS_AGREE | E4 caseHOST_TIERS_AGREE, two rows: the tier arrays and `all` disagree; codex leaves every tier while still dispatched. `check_host_tiers` fails naming `install.sh` | tests/test-seed-lint.sh | unit | green |
| SESSION_RECORD_FORM_IS_PLACED | S9 inside case_plan_records: a fresh `install.sh claude-code` holds `docs/graph/plans/sessions/_session-record.template.md` byte-identical to the seed's form; after a plant record and an edit to the placed form, `install.sh all` leaves both byte-identical, with no backup beside either | tests/test-plant-state.sh | integration | green |
| ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE | X383 case_engine_reconcile_stale_grill_lint: a stale `grill-lint.py` (the seed's copy with every line naming `waves` removed), reconciled with no `--preserve`, exits 0, equals the seed's file byte for byte, and leaves one `.bak-*` holding the older body | tests/test-graft-tools.sh | unit | green |
| ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE | X384 case_engine_reconcile_spec_lint_keeps_test_globs: a `spec-lint.py` with the plant's own `TEST_GLOBS` and an older body, reconciled with no `--preserve`, exits 0, keeps the plant's `TEST_GLOBS` and adopts the seed's body | tests/test-graft-tools.sh | unit | green |
| ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE | X385 case_engine_reconcile_explicit_preserve_wins: `--preserve=ROOT_ID` on a `graph-lint.py` whose plant changed `ROOT_ID` and `KIND_PREFIX` keeps the plant's `ROOT_ID` and takes the seed's `KIND_PREFIX`; guard | tests/test-graft-tools.sh | unit | green |
| ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE | X386 case_engine_reconcile_other_name_takes_graph_lint_set: the same plant file named `project-lint.py`, reconciled with no `--preserve`, exits 0 and keeps both `ROOT_ID` and `KIND_PREFIX`; guard | tests/test-graft-tools.sh | unit | green |
| ENGINE_AUDIT_CHECKS_EVERY_PAIR | X387 case_engine_audit_one_line_per_pair: `graft-audit.py` with two `--engine` pairs, a current `graph-lint.py` and a stale `grill-lint.py`, prints two engine-currency lines, the current one naming `graph-lint.py` and the `graph engine STALE` one naming `grill-lint.py` | tests/test-graft-tools.sh | unit | green |
| ENGINE_AUDIT_CHECKS_EVERY_PAIR | X388, a row inside X389: a current pair then a malformed one exits non-zero and says `--engine wants <plant-file>:<seed-file>`, where the current pair alone exits 0; guard | tests/test-graft-tools.sh | unit | green |
| ENGINE_AUDIT_CHECKS_EVERY_PAIR | X389 case_engine_audit_malformed_first_pair_fails: a malformed pair then a current one exits non-zero and says `--engine wants <plant-file>:<seed-file>` | tests/test-graft-tools.sh | unit | green |
| EXISTING_PLANT_RECEIVES_CURRENT_ENGINES | S10 case_engine_upgrade: re-install leaves the older `grill-lint.py`. The reconcile half is held by X383 and the audit half by X387, both in `tests/test-graft-tools.sh` | tests/test-plant-state.sh | integration | green |
| ENGINE_LEFT_STALE_BY_GRAFT | X387 case_engine_audit_one_line_per_pair: the stale pair's `graph engine STALE` line names `grill-lint.py`, beside the current pair's line | tests/test-graft-tools.sh | unit | green |
| PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION | K7 case_k7_prior_kernel_fast_forwards: a kernel byte-identical to `core/AGENTS.md` at an earlier commit of a temp `git clone --local` of the seed is replaced with one backup holding it, no adopted-instructions row for that backup, no `OVERWRITTEN` line, a log line naming an earlier seed kernel; a second run files no row | tests/test-install-kernel-modes.sh | integration | green |
| PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION | K7 case_k7_sweep_skips_prior_kernel_backup: a `CLAUDE.md.bak-*` holding an earlier seed kernel beside an installed plant gets no row from the next run's orphan sweep | tests/test-install-kernel-modes.sh | integration | green |
| PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION | K7 case_k7_plant_line_is_still_filed: an earlier seed kernel with one plant line added is filed and announced `OVERWRITTEN`; guard | tests/test-install-kernel-modes.sh | integration | green |
| SEED_HISTORY_UNAVAILABLE | K7 case_k7_no_history_falls_back: from a seed copy with no `.git`, an earlier seed kernel is filed for migration and exactly one log line names the missing history | tests/test-install-kernel-modes.sh | integration | green |
| RECREATED_LIST_IS_COMPLETE | D5 case_d5_recreated_list: twelve deleted protocol nodes re-created; `.cypress/recreated-nodes.txt` holds the §6 header (checked by its prefix) and all twelve paths, sorted and unique; the console prints ten and names the file | tests/test-install-adoption.sh | integration | green |
| RECREATED_LIST_IS_COMPLETE | D5 case_d5_fresh_list, the first check of case_d5_recreated_list: a first install writes `.cypress/recreated-nodes.txt` with the §6 header alone (checked by its prefix); guard, red under a mutant that records nodes on a first install | tests/test-install-adoption.sh | integration | green |
| RECREATED_LIST_IS_COMPLETE | D5 case_d5_recreated_list, third check: after the run that re-created twelve nodes, a run that re-creates nothing rewrites the file with the header line alone | tests/test-install-adoption.sh | integration | green |
| UNKNOWN_STAMP_KEYS_SURVIVE | S11 case_stamp_keys: a string key and an object key the installer does not own survive `install.sh all` JSON-equal, in their original order, after the installer's keys; `legal_corpus` and `tools` keep their own rules | tests/test-plant-state.sh | integration | green |
| STAMP_NOT_AN_OBJECT | S11 case_stamp_keys, second arm: a stamp that is a JSON array is moved to a `seed.json.bak-*`, a stamp is written from the installer's keys, one line names the backup. The arm runs after the first, so its red is not observed until the first arm is green | tests/test-plant-state.sh | integration | green |
| STAMP_NOT_AN_OBJECT | S12 inside case_s7: a stamp that does not parse (cut off inside a field; bytes that are not UTF-8) is not the trigger: the run exits non-zero with the preflight's refusal line, the stamp is byte-identical, no `seed.json.bak-*` is made, the file listing is unchanged. The truncated arm is a guard; the not-UTF-8 arm is red: the preflight's reader stops on a Python traceback, not its refusal | tests/test-plant-state.sh | integration | green |
| PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX | E5 case_pre_growth_pointer, first check: a fresh `install.sh claude-code` gives `docs/graph/index.md` one pre-growth block, delimited as §6 gives, naming `EXPERT_SEED_INSTALL_PROMPT.md` and `protocol.initialize` | tests/test-full-install.sh | integration | green |
| PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX | E5 case_pre_growth_pointer, second check: the placed `CLAUDE.md` names neither `EXPERT_SEED_INSTALL_PROMPT.md` nor `protocol.initialize` | tests/test-full-install.sh | integration | green |
| PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX | E5 case_pre_growth_pointer, third check: a re-install over an index with no pre-growth block leaves it byte-identical; guard | tests/test-full-install.sh | integration | green |
| CODE_ANCHOR_TOOL_IS_PLACED | E6 case_code_anchor_tool: a fresh `install.sh all` places `docs/graph/code-anchor.py` byte-identical to `tools/code-anchor.py` and writes no `.cypress/anchor.json`. The second check, a re-install over an older copy leaving a backup, is held by the M7 sweep of `tests/test-install-placement.sh`, whose discovered destination set holds the tool | tests/test-full-install.sh | integration | green |
| EVERY_BACKUP_IS_CLASSIFIABLE | X390 case_audit_plant_agent_projection (GA-C3): a `.claude/agents/<name>.md` backup whose plant node `docs/graph/agents/<name>.md` has `origin: project` is not UNMAPPED and the audit exits 0; a projection backup with no seed source and no plant node stays UNMAPPED, exit 1 | tests/test-graft-tools.sh | unit | green |
| EVERY_BACKUP_IS_CLASSIFIABLE | X391, a row of X390: a `.claude/skills/<name>/SKILL.md` backup whose plant node `docs/graph/skills/<name>.md` has `origin: project` is not UNMAPPED and the audit exits 0; a skill projection backup with no plant node stays UNMAPPED, exit 1 | tests/test-graft-tools.sh | unit | green |
| EVERY_BACKUP_IS_CLASSIFIABLE | X392, a row of X390: a `.github/agents/<name>.agent.md` backup whose plant node `docs/graph/agents/<name>.md` has `origin: project` is not UNMAPPED and the audit exits 0; a Copilot agent view backup with no seed agent and no plant node stays UNMAPPED, exit 1 | tests/test-graft-tools.sh | unit | green |
| MODEL_MAP_TEMPLATE_IS_PLACED | E7 case_model_map_placed: a fresh `install.sh claude-code` holds `docs/graph/models.md` byte-identical to `templates/docs/models.md`; after a plant edit to it, `install.sh all` leaves it byte-identical with no backup beside it; guard: the existing scaffold walk places the template, so the case passes on arrival once `templates/docs/models.md` exists, and is held by the mutant that deletes that template | tests/test-full-install.sh | integration | green |
| OPENCODE_MODEL_FROM_MAP | E8 case_opencode_model_from_map: a map filling the opencode cells of the authoring-high and investigation-medium rows, then `install.sh opencode`: an opus/high agent and a sonnet/medium agent each equal their graph home with only the `model:` line replaced by the cell; under `--symlink` the projection is a regular file; the stamp's opencode entry is `"verbatim": false`; a plant agent with `model: haiku` and `effort: high` gets the investigation-low cell | tests/test-full-install.sh | integration | green |
| OPENCODE_NO_MAP_ROW_NO_MODEL_LINE | E9 case_opencode_no_map_row: a fresh `install.sh opencode` exits 0 and every projection equals its graph home with the `model:` line removed; stdout has one line naming `docs/graph/models.md` and the count; with other rows filled, an agent whose row is `-`, one whose row is missing and a plant agent with `model: inherit` carry no `model:` line, a plant agent with `model: provider-q/model-q` keeps that value (copied as is), and stdout has exactly one line `opencode: <n> of <total> agents carry no model: line`, where the two numbers differ | tests/test-full-install.sh | integration | green |
| OPENCODE_MAP_UNREADABLE_FAILS_CLOSED | E10 case_opencode_map_unreadable: over an installed opencode plant whose authoring-high cell is filled and projected, a change to that cell plus a map row with class `premium` makes `install.sh opencode` exit non-zero with stderr naming `docs/graph/models.md`; every `.opencode/agents/*.md` is byte-identical to the snapshot taken before the run and no new `.bak-*` is beside any, so a run that projects before it refuses fails the case | tests/test-full-install.sh | integration | green |
| MODEL_MAP_UNREADABLE | E10 case_opencode_map_unreadable (the same case holds the refusal and the untouched projections) | tests/test-full-install.sh | integration | green |
| OPENCODE_SELECTOR_UNRESOLVED | (no behavioural test: the installer has no host catalog to check a cell against; §7) | — | — | pending |
| OPENCODE_CHECK_DETECTS_DRIFT | E11 case_opencode_check_drift: over an opencode plant with a filled authoring-high cell, `install.sh opencode --check` exits 0 and says up to date; after a hand edit to one projection, and after a cell edit with no re-run, it exits non-zero naming the stale projections; `install.sh all --check` fails the same way; the plant's file digest is unchanged by every run | tests/test-full-install.sh | integration | green |
| MODEL_MAP_UNREADABLE | E11 case_opencode_check_drift, its last arm: a map row with class `premium` makes `install.sh opencode --check` exit non-zero with stderr naming `docs/graph/models.md` | tests/test-full-install.sh | integration | green |
| SEED_ONLY_FILES_NEVER_PLACED | X393 check_seed_only_stays_home: a copied `manifest.json` whose `tools` map gains `tools/prepare-release.py` is a finding naming that path as a seed-only file | tests/test-seed-lint.sh | unit | green |
| SEED_ONLY_FILES_NEVER_PLACED | X394 check_seed_only_stays_home: a copied `install.sh` that places a file from `$SEED_ROOT/docs/` that is not itself seed-only (`docs/decisions/index.md`) is a finding naming `install.sh` that says it sources a file under `$SEED_ROOT/docs` | tests/test-seed-lint.sh | unit | green |
| SEED_ONLY_FILES_NEVER_PLACED | X395 check_seed_only_stays_home: a copied `manifest.json` whose `tools` map drops `tools/code-anchor.py`, which `install.sh` places, is a finding naming `manifest.json` | tests/test-seed-lint.sh | unit | green |

Coverage note, so the table is not read as more than it is.

**The engine rows (7.31.0).** Every case of `tests/test-graft-tools.sh`, X383
to X389 among them, runs under one collector, so each label shows its own
result in one run. A row marked guard passes on the unmodified tools and is held
by a named mutant instead of an observed red: X385 by an explicit `--preserve`
ignored, X386 by an unknown engine name given no preserve set, X388 by a later
malformed pair skipped. EXISTING_PLANT_RECEIVES_CURRENT_ENGINES is held in
two halves: S10 `case_engine_upgrade` in `tests/test-plant-state.sh` holds the
re-install, and X383 and X387 hold the reconcile and the audit.

**The 7.32.0 rows.** K7, D5, S11, E5 and E6 are the RED of the five
contracts and two failures promoted from the 7.32.0 pending block. K7's four
cases run in one collecting block at the end of
`tests/test-install-kernel-modes.sh`, so each shows its own result; the other
suites run each case as its own scenario. E5, E6 and D5 are one scenario per
contract, and each check in it reports its own result. A row marked guard passes on the
unmodified installer. K7's seed is a temp clone of the real seed; when the
checkout is shallow and holds no earlier kernel, the clone gains an earlier
body and the current one as two commits, so the case still has a history to
walk.

**The 7.35.0 rows.** E7 to E11 and X393 to X395 were written ahead of their
RED (adr-0021, adr-0022). E7 is a guard, `green` on arrival, because placing
the template needs no installer change. Every other row was `red` until the
tester's case landed and showed its failure on the tree it was written against;
the label is written as a comment inside its case, beside the slug. All of them
turned green in the round's GREEN wave (increments 19 and 21). E8 to E11
run in `tests/test-full-install.sh`, and the M9 exception list of
`tests/test-install-placement.sh` (`is_generated`) gained `.opencode/agents/*`
in the same RED, because `SYMLINK_MODE_IS_UNIFORM` already exempts generated
content and the opencode projections are generated. D3's second arm moved
its setup from `install.sh all codex` to `install.sh claude-code codex` in the
same RED: `all` records opencode, which `--check` checks, so the old setup
would no longer be a plant with no views in scope. The edited arm is green
before and after the installer change. The one `pending` failure row,
OPENCODE_SELECTOR_UNRESOLVED, has no test by design: it needs a host catalog
the installer does not have.

**M1 shares a label with a different invariant.** `tests/test-install-placement.sh`
carries cases headed `M1 completeness` and exits `M1 VIOLATED`, but what they
assert is that every machinery node the seed owns *arrives* in the plant — not
this spec's M1 (one canonical write mechanism). `seed-lint`'s
`check_spec_test_mapping` only greps for the label, so the divergence passes.
Read the two as separate claims until one is renamed; this spec's M1 is covered
the way M5 is, below.

**M5** (generated and copied files share destination safety) has no test of its
own and needs none: the M7 and M2 sweeps run over the destination set
*discovered* from a real install, which includes every generated file, so a
bypass or an unsafe generated write fails them by construction. This spec's M1
is covered by the same sweeps, for the same reason.

**M6** (generation completes before replacement) has no regression — proving it
needs a fault injected mid-generation, which is the same missing harness §11
records for PARTIAL_CORPUS.

**M10** (no write escapes PROJECT_DIR) is enforced by
`tests/test-install-placement.sh`'s target-containment case and is the
mechanism behind AC-2 and the §5 security NFR, both of which map only to the
narrower M2 above.

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| PARTIAL_CORPUS has no regression | The check was corrected from `-ge` over files to `-eq` over pages, but `place_tree` never fails partway, so no public-interface sequence produces the partial corpus the old check waved through | The correction is right and untested; it becomes testable when placement can fail mid-tree (ENOSPC, permission fault) | seed-installer | a fault-injection harness, if one is ever justified |

## 12. Changelog

This section did not exist before 2026-09-16. It was added with the entry
below rather than the correction being made silently, because a spec that is
edited to match the code without saying so is the drift kernel §4 forbids.
The file carries no version field; `status_date` in the frontmatter is the
only version surface it has, and it moves with each entry here.

- 2026-09-13 — written as `back-written` over existing installer behaviour.
  Sign-offs recorded as not owed; see §0.
- 2026-09-16 — §5 **Compatibility** corrected. The line read "POSIX shell and
  `python3` only", which was false about the code: `install.sh:1` is
  `#!/usr/bin/env bash` and `:69` uses `set -euo pipefail`, whose `pipefail`
  POSIX's `set` does not define, and all 30 shell files in this tree declare a
  bash shebang. Per the kernel's rule that a spec is never silently changed to
  match code, this is the SPEC being wrong about the code: the claim was
  corrected deliberately, `status_date` moved to this date, and the original
  wording is quoted above so the correction is not silently absorbed. No
  contract in §4, no data shape in §6 and no failure mode in §7 changed. The
  bash-versus-POSIX distinction itself is owned by a grown plant's
  `docs/graph/best-practices/bash.md` §"Two floors, not one" and is linked,
  not restated.
- 2026-09-23: host support tiers,
  [ADR-0009](../decisions/adr-0009-host-support-tiers.md). §2 and §3 name
  which hosts `all` installs; §4 gains six contracts written ahead of the code,
  with their RED at `9ca5900` (ALL_EXCLUDES_LEGACY_HOSTS,
  LEGACY_INSTALL_PRINTS_DEPRECATED, LEGACY_INSTALL_STILL_SUCCEEDS,
  ALL_NAMES_SKIPPED_FROZEN_HOSTS, CHECK_WITHOUT_COPILOT_SAYS_SO,
  HOST_TIERS_AGREE); §7 gains FROZEN_PROJECTION_LEFT_STALE; §10 binds each to
  its case. No existing contract changed. The status stays `back-written`
  for now: `active` needs product, architect and tester sign-offs under
  spec-lint, none is recorded for this increment, and §0 already records what
  a sign-off written to satisfy the linter did to this spec once before.
- 2026-09-23: review fixes, RED at `dd3e65c`. §4 gains
  ALL_CHECK_INCLUDES_RECORDED_COPILOT: `all --check` checks the Copilot views
  of a plant whose record carries github-copilot, so a CI job that ran it
  before 7.27.0 still fails on drift, and the DEPRECATED notice fires for that
  run because it acts on a frozen host. CHECK_WITHOUT_COPILOT_SAYS_SO's Given
  narrows from any target to a target whose record lacks github-copilot; the
  earlier Given blessed an exit 0 that hid a real check. HOST_TIERS_AGREE
  gains the duplicate-row, dispatchable-tool and `EVERY_HOST` clauses. §7
  FROZEN_PROJECTION_LEFT_STALE now says what the code prints, one `WARNING`
  line per host, and excludes a host the run checks. `status_evidence` names
  the two suites that already held contracts here and were missing from it.
  The status stays `back-written`; the owner decision in the entry above is
  still pending.
- 2026-09-23: review minor m1. HOST_TIERS_AGREE's dispatch clause reads every
  label of the `case "$tool"` block rather than lines shaped
  `<tool>) install_<tool> ;;`, which left `cursor) install_cursor || true ;;`
  green, and refuses a label that is not a bare tool name. A new And-clause
  holds the argument parser's accepted tools to the arrays plus `all`.
  Review minor m2: §10's ALL_CHECK_INCLUDES_RECORDED_COPILOT row now names
  the assertion that pins "fires, once". No other contract changed.
- 2026-09-28: 7.31.0 session record,
  [ADR-0013](../decisions/adr-0013-harness-memory-is-not-a-home.md). §4 gains
  SESSION_RECORD_FORM_IS_PLACED: every plant receives the session-record form,
  and so the `docs/graph/plans/sessions/` directory, through the existing
  scaffold walk. It adds no installer code and no write site, and a plant's own
  records are never touched. It is written ahead of its RED
  (`tests/test-plant-state.sh`), and §10 binds it when that RED lands. No
  existing contract changed; the status stays `back-written`.
- 2026-09-28: 7.31.0 plant pickup,
  [ADR-0014](../decisions/adr-0014-graft-reconciles-every-graph-engine.md).
  §1 and §2 take in the graph-engine reconciliation and the audit's engine
  check, the one write graft's tools make into a plant's placed engines; graft
  as a whole stays out of scope. §4 gains ENGINE_RECONCILE_PICKS_CONFIG_BY_ENGINE,
  ENGINE_AUDIT_CHECKS_EVERY_PAIR and EXISTING_PLANT_RECEIVES_CURRENT_ENGINES,
  written ahead of their RED (`tests/test-graft-tools.sh`,
  `tests/test-plant-state.sh`); §7 gains ENGINE_LEFT_STALE_BY_GRAFT. No
  installer behaviour and no existing contract changed; the status stays
  `back-written`.
- 2026-09-28: 7.31.0 §10 rows. S9 (`case_session_records`) flips to `green`.
  X383 to X389 bind the engine contracts in `tests/test-graft-tools.sh`: X383,
  X384, X387 and X389 are `red`, and X385, X386 and X388 are guards that are
  green on arrival. EXISTING_PLANT_RECEIVES_CURRENT_ENGINES carries a `pending`
  row until its RED lands in `tests/test-plant-state.sh`, and
  ENGINE_LEFT_STALE_BY_GRAFT has a row of its own.
- 2026-09-28: 7.31.0 final status pass. The graft-tool increment landed, and
  the final tip ran every step green with nothing carried or left unrun. X383,
  X384, X387 and X389 flip `red` → `green`; the guards X385, X386 and X388 stay
  `green`; EXISTING_PLANT_RECEIVES_CURRENT_ENGINES is bound by S10
  `case_engine_upgrade` in `tests/test-plant-state.sh` and is `green`, and so
  is ENGINE_LEFT_STALE_BY_GRAFT through X387. `status_date` moves to this entry,
  and `status_evidence` gains `tests/test-graft-tools.sh`, which holds three
  of the engine contracts and the failure row. One recorded limit: X386's
  mutant is first killed by an older case of `tests/test-graft-tools.sh` that
  exercises the same fallback and aborts before the collecting block, so the
  suite run does not show X386 killing it on its own (verified by hand). A
  candidate for a later round converts the older cases to the collecting
  pattern. No contract changed; the status stays `back-written`.
- 2026-09-28: 7.32.0 harvest, written ahead of its RED tests. §4 gains a block
  of pending amendments: five contracts (PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION,
  RECREATED_LIST_IS_COMPLETE, UNKNOWN_STAMP_KEYS_SURVIVE,
  PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX,
  CODE_ANCHOR_TOOL_IS_PLACED), two failure modes (SEED_HISTORY_UNAVAILABLE,
  STAMP_NOT_AN_OBJECT) and the §6 shapes they need. They are headed so that
  `spec-lint.py` counts none of them, and each moves to §4 or §7 as a
  `### Contract:` or `### Failure:` heading in the commit that lands its RED
  (`verify.status-evidence`), with its §10 row. This departs from the 7.31.0
  practice, which wrote contracts live ahead of their RED and carried the
  over-budget coverage line as expected-red at each tip. No existing contract
  changed; the status stays `back-written`.
- 2026-09-28: 7.32.0 RED. The pending block of §4 is gone: its five
  contracts are now `### Contract:` headings in §4
  (PRISTINE_PRIOR_KERNEL_IS_NOT_MIGRATION, RECREATED_LIST_IS_COMPLETE,
  UNKNOWN_STAMP_KEYS_SURVIVE, PRE_GROWTH_POINTER_LIVES_IN_THE_PLACEHOLDER_INDEX,
  CODE_ANCHOR_TOOL_IS_PLACED), its two failures are in §7
  (SEED_HISTORY_UNAVAILABLE, STAMP_NOT_AN_OBJECT), its shapes are in §6, and §2
  gains the three scope lines it named. §10 binds each to its RED case: K7,
  D5, S11, E5 and E6, `red` except the two guards. The contract text did not
  change in the move. No installer behaviour changed; the status stays
  `back-written`.
- 2026-09-28: 7.32.0 rulings on the RED, no installer behaviour changed. By
  the owner's decision, STAMP_NOT_AN_OBJECT's trigger narrows to a stamp that
  parses as JSON with a top level that is not an object. An empty stamp, a
  stamp that is not JSON, and one whose owned keys have the wrong type stay
  refused before any write by the installer's preflight (S7 unchanged).
  §9 gains AC-9 to AC-13 for the five contracts that left the pending block.
  The status stays `back-written`.
- 2026-09-28: 7.32.0 plant-owned projections. §10 binds
  EVERY_BACKUP_IS_CLASSIFIABLE to three cases of `tests/test-graft-tools.sh`.
  X390 is the GA-C3 case under a label the seed-lint binder reads, and it is
  `green`. X391 (the skill projection of a plant skill node) and X392 (the
  Copilot view of a plant agent node) are `red`: the audit reports each backup
  UNMAPPED. No contract changed; the status stays `back-written`.
- 2026-09-28: 7.32.0 docs pass, no installer behaviour changed.
  BACKUP_BEFORE_REPLACE's And-clause named `.cypress/seed.json` as the only
  exception, while `place_state` also writes `.cypress/recreated-nodes.txt`
  with no backup (RECREATED_LIST_IS_COMPLETE; ruling Q2.1 of the round's second
  question batch). The clause now names both. The spec was wrong about the code;
  no other contract changed, and the status stays `back-written`.
- 2026-09-29 — new contract `PREFLIGHT_SCOPED_TO_WRITTEN_TREES`, and the
  enumeration sentence under `PREFLIGHT_REFUSES_BEFORE_WRITING` corrected. The
  preflight walked every directory under the project root, so root-owned
  directories left by Docker in `node_modules/`, `.next/` or a data volume
  refused every install of that plant, though the installer never writes there.
  The walks now cover the written trees only. The earlier text said "beneath the
  target at any depth", which described the code and not the promise it exists
  for: a refusal that writes nothing. `status_date` moved to this date.
- 2026-09-29 — test consolidation (`docs/plans/grill-test-consolidation.md`,
  S1). HOST_TIERS_AGREE drops its clauses on the tier table of
  `documentation/host-capability-matrix.md`: the arrays in `install.sh` are the
  one home, and a published copy is no longer held to them. The dispatch,
  argument-parser and `EVERY_HOST` clauses stay. E4 keeps two planted rows (the
  arrays against `all`, and a dispatched tool in no tier); the other clauses
  run on the real tree and are no longer planted. §10 follows the folds of the
  consolidation: M9 in case_symchurn; D1 in case_block_declared and
  case_block_readonly; S9 in case_plan_records; S12 in case_s7; X388 in X389;
  X391 and X392 as rows of X390, which also holds M8's UNMAPPED arm;
  EXISTING_PLANT_RECEIVES_CURRENT_ENGINES's S10 row cites X383 and X387 for the
  reconcile and audit halves; the second check of CODE_ANCHOR_TOOL_IS_PLACED is
  the M7 sweep; the recreated
  list's header is checked by its prefix; the DEPRECATED count of
  ALL_CHECK_INCLUDES_RECORDED_COPILOT is held by E2. No installer behaviour
  changed; the status stays `back-written`.
- 2026-09-29: consolidation close-out, by the docs-librarian (spawn
  `session.10.docs-librarian.1`). §10 text only: the M10 row names the two
  paths the case now covers, the E2 row names E1 as the holder of the
  maintained-host negative, and the E3 row says two destinations each. No
  contract changed.
- 2026-09-30: 7.35.0, written ahead of its RED tests
  ([ADR-0021](../decisions/adr-0021-seed-only-procedures-stay-home.md),
  [ADR-0022](../decisions/adr-0022-the-plant-model-map.md)). §2 takes in the
  plant's model map and the seed-only files. §4 gains five contracts, live
  from this entry: MODEL_MAP_TEMPLATE_IS_PLACED (the map template, placed only
  when missing), OPENCODE_MODEL_FROM_MAP, OPENCODE_NO_MAP_ROW_NO_MODEL_LINE and
  OPENCODE_MAP_UNREADABLE_FAILS_CLOSED (the opencode projection writes its
  `model:` line from the map, or none, and refuses a map it cannot read), and
  SEED_ONLY_FILES_NEVER_PLACED (seed-lint holds the seed-only files and the
  manifest's `tools` map against `install.sh`). §6 gains the map grammar, the
  projection rule and the opencode stamp entry; §7 gains MODEL_MAP_UNREADABLE,
  OPENCODE_SELECTOR_UNRESOLVED and OPENCODE_PROJECTION_DRIFT_UNCHECKED; §9
  gains AC-14 to AC-17; §10 gains E7 (a guard, `green` on arrival) and E8 to
  E10 and X393 to X395, `red` until their RED lands, and two `pending` failure
  rows; §11 gains the opencode
  `--check` question. Until the RED lands, `spec-lint.py` counts these five
  contracts as uncovered and `seed-lint` reports each label as absent from its
  test file; both clear when the tester's cases name them. The contracts are
  written live, as in 7.31.0, because the round's RED batch lands before any
  GREEN and a pending block would need a second spec edit in that batch. No
  existing contract changed; the status stays `back-written`.
- 2026-09-30: 7.35.0, the session's rulings S1 and S3 on the architect's first
  findings (kept with the round's working records outside the seed), applied
  before any test of the entry above was written; the round's plan of record is
  `docs/plans/grill-7.35.0-positive-voice.md`. S1: a graft pickup that reports
  "none drifted" after checking nothing is a green that asserts nothing
  (`rule.verify`), so `install.sh opencode --check` is built. §4 gains
  OPENCODE_CHECK_DETECTS_DRIFT, which replaces the failure
  OPENCODE_PROJECTION_DRIFT_UNCHECKED and its §11 question, both removed.
  CHECK_WITHOUT_COPILOT_SAYS_SO's Given narrows to a record that carries
  neither github-copilot nor opencode, because `all --check` now checks the
  opencode projections of a plant that records opencode; its D3 case moves
  its second arm's setup to `install.sh claude-code codex`. §2, §3 and §6 name
  the check and its scope; MODEL_MAP_UNREADABLE also covers `--check`. S3:
  agent-lint's token set is every alias Claude Code accepts (SPEC-0005), so §6
  reads `haiku` as the `investigation | low` row and writes no model line for
  `inherit`, and OPENCODE_MODEL_FROM_MAP and OPENCODE_NO_MAP_ROW_NO_MODEL_LINE
  each gain that clause. §9 gains AC-18; §10 gains E11's two rows, `red`, and
  keeps one `pending` failure row. `spec-lint.py` counts six new contracts as
  uncovered until the RED lands. The status stays `back-written`.
- 2026-09-30: 7.35.0, the post-review fix pass (text only; no contract added
  or removed). §6: a plant declines the map by renaming it by hand, because
  `graft-audit.py --rename` leaves `models.md` in place since ruling S4.
  §7 MODEL_MAP_UNREADABLE's trigger names the refusals the renderer already
  makes: a map that is not UTF-8, a missing separator row, a row without four
  cells, and a `models.md` symlink leaving the target. §10: the 7.35.0 note is
  in the past tense, and the E9, E10, X393 and X394 rows describe the
  strengthened cases (E9's copy-through and count arms; E10's filled-cell
  setup; the needles X393 and X394 pin). The status stays `back-written`.
