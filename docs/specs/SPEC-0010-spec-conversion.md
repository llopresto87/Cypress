---
status: implemented
status_date: 2026-11-10
owner: architect
status_evidence: tests/test-spec-convert.sh (X640 to X643, X649) and tests/test-graft-tools.sh (X644 to X648), both wired into tests/run.sh, every §10 row green over the 9 contracts; each case was seen failing first, on the missing tool, the engine reconcile that dropped SKIP_DIRS, the audit that read a conversion backup as unmapped, or the graft run that recorded no baseline; X646 is a guard and passed on the base
---

# SPEC-0010: converting a plant to the kinds form, and what a graft carries with it

## 0. Metadata

- **Identifier:** SPEC-0010-spec-conversion
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-11-10
- **Last reviewed:** 2026-11-10
- **Related grill section:** docs/plans/grill-8.5.0-tester-surfaces.md, step T12
  (conversion, the first baseline, engines by graft)
- **Related ADRs:** adr-0034-a-test-is-owed-only-where-it-can-catch-something
  (conversion is a shape migration the steward ratifies; graft and grow remove
  no test); adr-0003-enforcement-layering-honesty (the audit class a ratified
  conversion leaves is reported, never silent)
- **Related specs:** SPEC-0009-worth-check (the baseline this graft records
  once); SPEC-0001-install-placement (an installed engine is never replaced by
  a plain re-install, so an engine reaches an existing plant by graft only)
- **Related wiki pages:** none (stdlib Python only)
- **Design latitude:** balanced. The owner decided on 2026-11-10 that the
  seed's own specs in today's form are converted in a later round, and that a
  grafted plant's baseline is decided per plant, with the baseline tests of a
  reopened spec listed for the owner's confirmation in that work
- **Supersedes:** none
- **Superseded by:** none
- **Sign-offs:** product [x] · architect [x] · tester [x]
  Product 2026-11-10: the owner's decisions of 2026-11-10 on the seed's own
  old-form specs and on the baseline of a grafted plant. Architect 2026-11-10:
  the round's surface definition of the conversion dry run and the baseline at
  graft, transcribed in §3, §4 and §6. Tester 2026-11-10: every case was
  written before the code it checks and seen failing for its own reason first;
  an independent tester's review is the open item of §11.

## 1. Summary

The kinds form gives each contract a `Check:` line, a declared-values table and
a §10 designed by risk. A plant's specs in the earlier form keep linting, and
converting one is a shape migration: graft proposes it, the steward ratifies it,
`tools/spec-convert.py` writes its mechanical part, and the plant's architect
does the judgment. The same graft carries the new engines onto the plant with
the plant's own test layout kept, and the graft that brings the worth check
records the plant's baseline once.

## 2. Scope

In scope: `tools/spec-convert.py` (seed-side, never placed in a plant), the
audit class its backup leaves, the reconcile of `spec-lint.py` and
`grill-lint.py` onto a plant with its own configuration, and the baseline step
of `tools/graft-run.py`.

Out of scope: the judgment of a conversion (re-labelling a contract `run`,
`review` or `covered`, a declared-values table, a risk-based §10, a trust path
set to yes); converting the seed's own specs (a later round); removing a test.

## 3. User-facing behavior

From the seed, `python3 tools/spec-convert.py --dry-run <plant>/docs/graph/specs/SPEC-NNNN-x.md`
prints what the conversion would add and what it leaves to the architect, and
writes nothing. After the steward ratifies, the same command with `--write
--steward-ratified` adds those lines, keeps the spec as it was beside it, and
says where. A graft rehearsal prints `worth: baseline holds N tests` in the
graft that brings the worth check, and names the plant's own baseline as left
as it is in any later graft.

## 4. Functional contracts

### Contract: SPEC_CONVERT_DRY_RUN_PRINTS_THE_MECHANICAL_PART
- **Given:** a plant spec in the earlier form
- **When:** `spec-convert.py --dry-run SPEC_PATH` runs, or the path alone
- **Then:** it prints the report of §8 for that spec: the two §0 lines to add,
  the count of contracts given `- **Check:** test` with each one's present
  mapping (its §10 row, and the slug in the tests the plant's `TEST_GLOBS` and
  `SKIP_DIRS` read), each contract already labelled kept as written, what stays
  unchanged and the judgment it leaves; it exits 0 and every file is unchanged

### Contract: SPEC_CONVERT_WRITE_NEEDS_THE_STEWARD
- **Given:** `--write`
- **When:** `--steward-ratified` or the spec path is missing
- **Then:** the run is refused with exit 2, the message names what is missing,
  and nothing is written

### Contract: SPEC_CONVERT_WRITES_ONLY_THE_MECHANICAL_PART
- **Given:** `--write --steward-ratified SPEC_PATH` on a spec in the earlier form
- **When:** it runs
- **Then:** the spec gains `- **Contract form:** kinds` and `- **Trust path:** no`
  in §0 and `- **Check:** test` in each unlabelled contract, every other line
  stays as it was and in its order, the spec as it was is kept once as
  `SPEC_PATH.bak-<YYYYmmdd-HHMMSS>`, and the plant's spec-lint reads each
  converted contract as kind test
- **And:** a second `--write` says the spec is already in the kinds form and
  writes nothing

### Contract: SPEC_CONVERT_NAMES_AN_UNRECOGNISED_SHAPE
- **Given:** a spec with no `### Contract:` heading, no `## 0.` section, a
  contract heading inside a code fence, or a file name that is not `SPEC-*.md`
- **When:** the tool runs in either mode
- **Then:** it prints `spec-convert: <file>: unrecognised spec shape: <each
  reason>; nothing written`, exits 1 and writes nothing; a path that does not
  exist exits 2 naming it

### Contract: SPEC_CONVERT_BACKUP_IS_AUDITED
- **Given:** a plant spec converted by the tool, and its backup
- **When:** `graft-audit.py` audits that backup's date
- **Then:** the backup is classed `SHAPE-MIGRATED` while the live spec is the
  backup plus the conversion's lines alone, and a knowledge overwrite once any
  other line differs

### Contract: GRAFT_ENGINE_KEEPS_THE_PLANT_TEST_LAYOUT
- **Given:** a plant whose `docs/graph/spec-lint.py` is the engine v8.4.0
  shipped, with its own `TEST_GLOBS` and `SKIP_DIRS`
- **When:** `graft-graph-engine.py` reconciles it with the seed's engine
- **Then:** the plant keeps its `TEST_GLOBS` and every member of its
  `SKIP_DIRS`, gains the seed's engine logic, and `graft-audit.py` reads the
  engine as current

### Contract: GRAFTED_ENGINES_LINT_AS_A_FRESH_INSTALL
- **Given:** a plant grafted from the v8.4.0 `spec-lint.py` and `grill-lint.py`
  and a fresh install with the same test layout, holding the same kinds-form
  spec, legacy specs, tests and plan
- **When:** each plant runs its own spec-lint and grill-lint
- **Then:** the two outputs and exit codes are identical, and both read the
  kinds form

### Contract: NEW_ENGINES_LINT_EXISTING_RECORDS_UNCHANGED
- **Given:** the seed's own specs that carry no form or Check line, and every
  `docs/plans/grill-*.md`
- **When:** the seed's current engines and the v8.4.0 engines each lint them
- **Then:** the outputs and exit codes are identical

### Contract: GRAFT_RECORDS_THE_FIRST_WORTH_BASELINE
- **Given:** a plant grown before the worth check, with read-back tests and no
  `docs/graph/worth-baseline.txt`
- **When:** `graft-run.py` rehearses the graft
- **Then:** the copy's `worth-check.py --write-baseline` runs once, the run
  prints `worth: baseline holds N tests`, no test file changes, and no item
  proposes a removal; a read-back test added afterwards fails the check
- **And:** a plant whose baseline is present keeps it byte for byte, the run
  says so, and the tests flagged outside it are one judgment item that proposes
  no write and no removal

## 5. Non-functional requirements

Stdlib Python, bash 3.2 for the tests. `spec-convert.py` reads the plant's
`TEST_GLOBS` and `SKIP_DIRS` with `ast.literal_eval` and never imports the
plant's engine. It is never placed in a plant and no install, graft step or
tool runs it. Nothing here adds to the kernel or to an always-loaded prompt.

## 6. Data shapes

### Command line

`spec-convert.py [--dry-run] SPEC_PATH [--root DIR]` and
`spec-convert.py --write --steward-ratified SPEC_PATH [--root DIR]`. `--root` is
the plant root; it defaults to three levels above a spec under
`docs/graph/specs/`. Exit 0: reported, written, or already in the kinds form.
Exit 1: unrecognised shape. Exit 2: usage, refused write, unreadable path.

### What the write adds

The §0 lines go before `- **Sign-offs:**`, else after the section's last
bullet; a `Trust path` line already there is kept. Each `- **Check:** test` goes
after the last bullet of its contract block and its continuation lines.

### The engine's configuration

`graft-graph-engine.py` keeps `TEST_GLOBS` and `SKIP_DIRS` for `spec-lint.py`;
`SKIP_DIRS`, a set, is unioned with the seed's members. `graft-audit.py`
excludes both from its engine-currency comparison.

## 7. Failure modes

### Failure: CONVERTED_SPEC_FAILS_THE_PLANT_LINT
- **Trigger:** a converted spec keeps its legacy §10, and the plant's
  spec-lint links a test-kind contract of a kinds-form spec by a §10 Covers row
  only
- **Response:** the plant's spec-lint names each such contract as covered by
  no §10 row
- **Recovery:** the architect writes the risk-based §10 in the work the
  steward ratified, or the engine accepts the legacy row (§11)

### Failure: BASELINE_HOLDS_A_TEST_THAT_CATCHES_NOTHING
- **Trigger:** the first baseline records the read-back tests a plant has
- **Response:** they are reported and do not fail the plant's check
- **Recovery:** the owner decides per plant; a reopened spec lists its
  baseline tests for the owner's confirmation

## 8. Examples

```
spec-convert: SPEC-0501-orders.md (legacy form -> kinds form) — DRY RUN, nothing written
 §0: add "- **Contract form:** kinds" and "- **Trust path:** no"   (set yes if a contract is security, data-integrity or money)
 §4: 3 contracts -> "- **Check:** test" each (present mapping kept as evidence: §10 row / slug in test)
    ORDER_TOTAL_IS_SUMMED: §10 row (test_order_total_is_summed, tests/test_orders.py); slug in test (tests/test_orders.py)
 unchanged: Given/When/Then, §7, §9, §10 header (legacy §10 stays valid), changelog
 judgment, NOT done here: re-labelling a contract run / review / covered, a declared-values table, a risk-based §10: the plant's architect, after the steward ratifies
```

## 9. Acceptance criteria

- [x] AC-1: the dry run reports the mechanical part and writes nothing; maps to
  SPEC_CONVERT_DRY_RUN_PRINTS_THE_MECHANICAL_PART
- [x] AC-2: the write needs the steward, adds only the mechanical lines with a
  backup, refuses an unknown shape and leaves an audited backup; maps to
  SPEC_CONVERT_WRITE_NEEDS_THE_STEWARD, SPEC_CONVERT_WRITES_ONLY_THE_MECHANICAL_PART,
  SPEC_CONVERT_NAMES_AN_UNRECOGNISED_SHAPE, SPEC_CONVERT_BACKUP_IS_AUDITED
- [x] AC-3: the engines reach a configured plant by graft, lint as a fresh
  install does, and lint the existing records unchanged; maps to
  GRAFT_ENGINE_KEEPS_THE_PLANT_TEST_LAYOUT, GRAFTED_ENGINES_LINT_AS_A_FRESH_INSTALL,
  NEW_ENGINES_LINT_EXISTING_RECORDS_UNCHANGED
- [x] AC-4: the graft that brings the worth check records the baseline once;
  maps to GRAFT_RECORDS_THE_FIRST_WORTH_BASELINE

## 10. Test mapping

(Owned by `tester`.) The conversion cases run on copies of
`tests/fixtures/spec-convert/plant`, whose engine `configure.py` gives the
plant's own test layout; the engine cases read the v8.4.0 engines from the tag.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| SPEC_CONVERT_DRY_RUN_PRINTS_THE_MECHANICAL_PART | X640 the report line by line, a run naming no mode, a partly labelled spec | tests/test-spec-convert.sh | integration (fixture) | green |
| SPEC_CONVERT_WRITE_NEEDS_THE_STEWARD | X641 no --steward-ratified, no spec path; the plant's digest unchanged | tests/test-spec-convert.sh | integration (fixture) | green |
| SPEC_CONVERT_WRITES_ONLY_THE_MECHANICAL_PART | X642 two specs written, the added lines alone, one backup, the engine's reading, a second write | tests/test-spec-convert.sh | integration (fixture) | green |
| SPEC_CONVERT_NAMES_AN_UNRECOGNISED_SHAPE | X643 no contract, no §0, a fenced contract, a missing path, --help | tests/test-spec-convert.sh | integration (fixture) | green |
| SPEC_CONVERT_BACKUP_IS_AUDITED | X649 SHAPE-MIGRATED after the write, a knowledge overwrite after one more line | tests/test-spec-convert.sh | integration (fixture) | green |
| GRAFT_ENGINE_KEEPS_THE_PLANT_TEST_LAYOUT | X644 the v8.4.0 spec-lint.py with its own layout, reconciled and audited | tests/test-graft-tools.sh | integration (tag) | green |
| GRAFTED_ENGINES_LINT_AS_A_FRESH_INSTALL | X645 a grafted plant and a fresh install, both lints, byte-identical | tests/test-graft-tools.sh | integration (temp install) | green |
| NEW_ENGINES_LINT_EXISTING_RECORDS_UNCHANGED | X646 the seed's legacy specs and every grill plan under both engine pairs | tests/test-graft-tools.sh | integration (tag) | green |
| GRAFT_RECORDS_THE_FIRST_WORTH_BASELINE | X647 the graft that brings the check; X648 a plant whose baseline is present | tests/test-graft-tools.sh | integration (stage) | green |
| CONVERTED_SPEC_FAILS_THE_PLANT_LINT | none: an engine question for the owner, §11 | none | none | none |
| BASELINE_HOLDS_A_TEST_THAT_CATCHES_NOTHING | none: the owner decides per plant | none | none | none |

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Should the plant's spec-lint accept a legacy §10 row as the link of a test-kind contract while a kinds-form spec has no risk table? | the surface definition keeps the legacy §10 valid after the mechanical conversion, and the engine reads only a Covers row in a kinds-form spec | the architect writes the risk-based §10 in the ratified work | owner | the round's review |
| Should an independent tester review these cases? | they were written by the spawn that built the tool | each was seen failing for its own reason first | tester | the round's review |

## 12. Changelog

- 2026-11-10 — created by `architect` from the round's surface definition of
  the conversion dry run and the baseline at graft, and the owner's decisions
  of 2026-11-10 (the seed's own specs converted in a later round; a grafted
  plant's baseline decided per plant). Nine contracts; each case written first
  and seen failing for its own reason, then green.
