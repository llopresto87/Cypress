---
status: back-written
status_date: 2026-09-16
owner: seed-installer
status_evidence: tests/test-install-placement.sh, tests/test-plant-state.sh, tests/test-install-kernel-modes.sh, tests/test-install-adoption.sh (all wired into tests/run.sh)
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
- **Last reviewed:** 2026-09-13
- **Related grill section:** docs/plans/grill-7.15.0-remediation.md §3, §5
- **Related ADRs:** adr-0003-enforcement-layering-honesty
- **Supersedes:** —
- **Superseded by:** —

## 1. Summary

What `install.sh` is allowed to do to a target directory. The seed's kernel
§3.1 says code without a spec is in remediation mode, and the installer — the
one component that writes into somebody else's repository — had no spec at all.
This contracts the properties that make an install safe to run twice, safe to
run over a customized plant, and safe to audit afterwards: every write is
recoverable, no write escapes the target, an identical re-run changes nothing,
and the record the installer keeps cannot contradict the filesystem.

## 2. Scope

- **In scope:**
  - every byte `install.sh` writes into `--project-dir`
  - the backup contract and what `--force` does and does not suppress
  - copy vs symlink placement, including the root kernel
  - `.cypress/seed.json` as the plant's persistent record
  - the legal corpus as a whole-or-nothing artifact
  - preflight refusal before any write
- **Out of scope:**
  - what the placed files MEAN (the graph schema, the kernel's content)
  - `grow`, `graft` and `harvest`, which are user-sovereign flows over an
    already-installed plant
  - the seed's own repository layout

## 3. User-facing behavior

An owner points the installer at a project and names one or more harnesses. The
installer either completes, or refuses before writing anything and says which
path is in the way. Running it again over an unchanged project does nothing and
says nothing. Running it over a project someone has edited replaces the seed's
own files, leaves a timestamped copy of every body it replaced, and names them.
Nothing outside the named project directory is ever modified.

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
- **And:** the only exception is `.cypress/seed.json`, which is installer-owned
  derived state, never authored by hand, and would otherwise accrue one backup
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
  already exists beneath the target at any depth, and every existing symlink
  beneath it — the last two walked rather than listed, so they do not depend on
  anyone remembering to add a path.

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

## 10. Test mapping

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| SINGLE_WRITER | M7 sweep over the discovered destination set | tests/test-install-placement.sh | integration | green |
| SINGLE_WRITER | check_install_write_sites — the exception set is exhaustive, by count as well as by shape | tests/seed-lint.py | unit | green |
| BACKUP_BEFORE_REPLACE | M7 sweep | tests/test-install-placement.sh | integration | green |
| SYMLINK_IS_REPLACED_NOT_FOLLOWED | M2 attack over every destination | tests/test-install-placement.sh | integration | green |
| IDENTICAL_RERUN_IS_INERT | M3 churn check (names the churned files) | tests/test-install-placement.sh | integration | green |
| SYMLINK_MODE_IS_UNIFORM | M9 link-uniformity check | tests/test-install-placement.sh | integration | green |
| EVERY_BACKUP_IS_CLASSIFIABLE | M8 audit-totality check | tests/test-install-placement.sh | integration | green |
| FORCE_SUPPRESSES_WARNING_NOT_BACKUP | M4: --force keeps every backup, and without it the backup is announced | tests/test-install-placement.sh | integration | green |
| ONE_KERNEL_BODY | K1/K4/K5 cases | tests/test-install-kernel-modes.sh | integration | green |
| COPY_MODE_ISOLATES | K2 case | tests/test-install-kernel-modes.sh | integration | green |
| SYMLINK_MODE_IS_UNIFORM | K3 case | tests/test-install-kernel-modes.sh | integration | green |
| DECISIONS_SURVIVE_SILENCE | S1 case | tests/test-plant-state.sh | integration | green |
| ADAPTERS_ACCUMULATE | S2/S5 cases, both orders | tests/test-plant-state.sh | integration | green |
| RECORD_AGREES_WITH_DISK | S6 refusal case | tests/test-plant-state.sh | integration | green |
| CORPUS_IS_WHOLE_OR_ABSENT | S6 whole-corpus case | tests/test-plant-state.sh | integration | green |
| CONTRADICTORY_CORPUS_TRANSITION | S6 refusal leaves disk and record untouched | tests/test-plant-state.sh | integration | green |
| PREFLIGHT_REFUSES_BEFORE_WRITING | D1 preflight refuses before any write (`.claude`-as-a-file, read-only target) | tests/test-install-adoption.sh | integration | green |
| SYMLINK_IS_REPLACED_NOT_FOLLOWED | M10 (6) a symlinked DIRECTORY leaving the target is refused at any depth, M10 (7) one staying inside still works — §5's Security NFR and §9 AC-2 rest on this | tests/test-install-placement.sh | integration | green |
| DESTINATION_PATH_OCCUPIED | D1 destination occupied by a non-directory | tests/test-install-adoption.sh | integration | green |
| TARGET_NOT_WRITABLE | D1 target directory not writable | tests/test-install-adoption.sh | integration | green |
| PARTIAL_CORPUS | (no behavioural test — see §11) | — | — | pending |

Coverage note, so the table is not read as more than it is.

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
