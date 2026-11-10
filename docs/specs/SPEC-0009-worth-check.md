---
status: implemented
status_date: 2026-11-10
owner: architect
status_evidence: tests/test-worth-check.sh (X580 to X592), wired into tests/run.sh, every §10 row green over the 13 contracts; each case was seen failing first on the missing tool, then passing against the fixture suite of tests/fixtures/worth/ and its hand-written verdict table
---

# SPEC-0009: the worth check

## 0. Metadata

- **Identifier:** SPEC-0009-worth-check
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-11-10
- **Last reviewed:** 2026-11-10
- **Related grill section:** docs/plans/grill-8.5.0-tester-surfaces.md, step T10
  (the worth check)
- **Related ADRs:** adr-0034-a-test-is-owed-only-where-it-can-catch-something
  (OD3: a test that catches nothing is removed, and graft and grow never remove
  a test); adr-0003-enforcement-layering-honesty (the check is detective, a
  heuristic that errs toward sparing); adr-0021 (the tools `install.sh` places
  are held against `manifest.json`)
- **Related specs:** SPEC-0001-install-placement (its placement contracts and
  destination sweep hold every file `install.sh` writes, this tool's copy
  included); SPEC-0007-source-index (the same `TEST_GLOBS` declaration, read the
  same way)
- **Related wiki pages:** none (stdlib Python only)
- **Design latitude:** balanced. The owner decided on 2026-11-10 that the
  check reads Python and TypeScript or JavaScript and reports every other
  language as not checked, and that a grafted plant's baseline is decided per
  plant after the owner sees it
- **Supersedes:** none
- **Superseded by:** none
- **Sign-offs:** product [x] · architect [x] · tester [x]
  Product 2026-11-10: the owner's decisions of 2026-11-10 on the languages read
  and on the baseline of a grafted plant, as the round's surface definition
  states them. Architect 2026-11-10: the round's surface definition of the worth
  check, which this spec transcribes in §3, §4 and §6. Tester 2026-11-10: the
  fixture suite and its verdict table were written before the tool and every
  case was seen failing on the missing tool first; an independent tester's
  review of the fixtures is the open item of §11.

## 1. Summary

ADR-0034 says a test that catches nothing is removed. The commonest such test
reads back a literal the same change adds: it is red while the line is absent
and green once it is present, so it proves only that the change is there. The
worth check, `tools/worth-check.py`, placed in every plant at
`docs/graph/worth-check.py`, reads a plant's tests and flags each one whose only
assertions read back a literal that way. It spares a test that feeds inputs to
logic, a regression test for a bug and a security negative control. It never
removes or edits a test: a flagged test is the owner's to remove, keep with a
reason, or leave in the plant's baseline.

## 2. Scope

In scope: the tool, its placement, the baseline file it writes, the keep line it
reads, and the gate row a plant adds to its verification runbook.

Out of scope: removing a test (ADR-0034 OD3 gives that to the unit of work that
created it, or to a batch the owner confirms); any language beyond Python and
TypeScript or JavaScript; running the check over this repository's own suite,
whose tests assert documentation text on purpose.

## 3. User-facing behavior

A plant runs `python3 docs/graph/worth-check.py` from its root. Each flagged
test is one line that names the test, the literal it reads back, how many
assertions it has, and the keep line to add if the test earns its place. A
summary line counts the flagged tests, the ones in the baseline, the files read
and the files not checked with their languages. When a flagged test is neither
kept nor in the baseline, a closing line says the run failed and what to do with
each test, and the exit code is 1. A plant whose `docs/graph/spec-lint.py` is
missing or sets no `TEST_GLOBS` gets one line saying the check is not
configured, and exit 0.

## 4. Functional contracts

### Contract: WORTH_FLAGS_A_READ_BACK_TEST
- **Given:** a Python, TypeScript or JavaScript test whose every assertion
  compares a literal with a value the test reads back unchanged: a declared
  constant, a config entry, or text read from a file
- **When:** the worth check reads it
- **Then:** the test is flagged with the line
  `path::name  reads back <literal> that the same file/change adds; only assertion(s): <n>; keep it with a line "<comment> worth-check: keep — <reason>" above the test if it earns its place`,
  where `<comment>` is the file's own comment syntax
- **And:** a flagged test that is neither kept nor in the baseline makes the run
  exit 1, and the closing line says to remove it, make it feed inputs to the
  logic it guards, or keep it with a reason

### Contract: WORTH_SPARES_LOGIC_TESTS
- **Given:** a test that calls the code under test, or exercises a pattern, a
  condition, an order of precedence or a computed value, or reads a file the code
  under test wrote, or compares two values with no literal between them
- **When:** the worth check reads it
- **Then:** the test is not flagged, and the `--json` report lists it as read,
  with verdict `spared` and the reason

### Contract: WORTH_SPARES_BUG_REGRESSIONS
- **Given:** a test whose comment directly above, comment inside, docstring,
  name or title names a bug, an issue, a regression or a ticket
- **When:** the worth check reads it, even with the shape of a read-back
- **Then:** the test is not flagged: a bug reproduction is always written and
  stays (ADR-0034)

### Contract: WORTH_SPARES_SECURITY_CONTROLS
- **Given:** a test that asserts a refusal or an absence (`not in`, `!=`,
  `is False`, `.not.`, an expected exception), or whose text is about security
- **When:** the worth check reads it
- **Then:** the test is not flagged

### Contract: WORTH_NEVER_FLAGS_BY_NAME_OR_LENGTH
- **Given:** a test whose name promises logic and whose body reads a value back,
  a read-back test with many assertions, a logic test that shares its name with
  a read-back, and a test with no assertion
- **When:** the worth check reads them
- **Then:** the verdict follows the assertions alone: the first two are
  flagged, the last two are not, and a test is never flagged without its
  assertions being read

### Contract: WORTH_UNREAD_FILE_IS_NOT_CHECKED
- **Given:** a test file in a language the check does not read, or a Python,
  TypeScript or JavaScript file that does not parse
- **When:** the worth check runs
- **Then:** the file is listed as `<path>  not checked (<language or reason>)`,
  the summary counts it under `not checked (languages: ...)`, and no output calls
  it or the run clean

### Contract: WORTH_UNCONFIGURED_PLANT_IS_NAMED
- **Given:** a plant with no `docs/graph/spec-lint.py`, or one that sets no
  `TEST_GLOBS`
- **When:** the worth check runs, with or without `--json` or `--write-baseline`
- **Then:** it prints
  `worth-check: not configured for this plant (set TEST_GLOBS in docs/graph/spec-lint.py)`,
  exits 0, writes nothing, and never prints the word clean

### Contract: WORTH_KEEP_MARKER_KEEPS_WITH_REASON
- **Given:** a comment line `worth-check: keep — <reason>`, in any comment
  syntax, directly above a test the check would flag
- **When:** the worth check runs
- **Then:** the test does not fail the run and the report prints
  `worth-check: kept: path::name — <reason>`
- **And:** a keep line with no reason keeps nothing, and the report says so on
  the test's own line

### Contract: WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS
- **Given:** a plant whose `docs/graph/worth-baseline.txt` holds the tests
  flagged on the day it was recorded
- **When:** the worth check runs
- **Then:** the tests in the baseline are reported and do not fail the run, and
  a newly flagged test outside it fails the run with exit 1
- **And:** the first `--write-baseline` records every test flagged that day,
  and a plant with no baseline file has an empty baseline

### Contract: WORTH_BASELINE_ONLY_SHRINKS
- **Given:** a baseline file exists
- **When:** `--write-baseline` would add a test to it
- **Then:** the write is refused with exit 1, the message names each test it
  would add and what to do with it, and the file is unchanged
- **And:** an entry that no longer flags is reported as shrinkable, and
  `--write-baseline` then drops it

### Contract: WORTH_BAD_INPUT_EXITS_2
- **Given:** an unknown option, a PATH that does not exist, a test file that is
  not UTF-8, or `--write-baseline` with a PATH
- **When:** the worth check runs
- **Then:** it exits 2 and names the option or path and the reason
- **And:** a PATH that exists narrows the read to that file or directory

### Contract: WORTH_NEVER_EDITS_A_TEST
- **Given:** any run of the worth check
- **When:** it finishes
- **Then:** every test file is byte for byte as it was, and nothing was written
  beside it; the only file the tool writes is the baseline

### Contract: WORTH_CHECK_IS_PLACED
- **Given:** a fresh install of any host
- **When:** the install finishes
- **Then:** `docs/graph/worth-check.py` is byte-identical to the seed's
  `tools/worth-check.py`, answers `--help` with the keep line and the gate row of
  the verification runbook, and in a plant with no tests reads nothing and exits 0

## 5. Non-functional requirements

Stdlib Python on the seed's Python floor, no third-party parser and no model.
The tool reads `TEST_GLOBS` and `SKIP_DIRS` with `ast.literal_eval` from the
plant's `spec-lint.py`, as `source-index.py` does, and never imports it. It
adds no configuration to any graph engine, so `tools/graft-graph-engine.py`'s
table is unchanged. It adds nothing to the kernel or to any always-loaded
prompt.

## 6. Data shapes

### Command line

`worth-check.py [--root DIR] [--baseline FILE] [--write-baseline] [--json] [--help] [PATH...]`.
`--root` defaults to the current directory; `--baseline` is read from the root
and defaults to `docs/graph/worth-baseline.txt`.

### What counts as a read-back

A Python test is a function named `test*` at module level or in a class; a
TypeScript or JavaScript test is a `test(` or `it(` call whose first argument
is a literal title. A test is flagged when all of these hold:

- every call in its body reads a value rather than computing one: a file read,
  a path join, a JSON parse, a string method on text already read, or the
  assertion itself;
- every name it reads is declared in the file or imported, never a parameter
  or fixture of the test and never a value set up elsewhere;
- it has at least one assertion, and every assertion compares at least one
  literal with such a value, with positive polarity;
- no comment, docstring, name or title marks it as a bug regression, and its
  text is not about security;
- no keep line with a reason sits directly above it.

### Output and exit codes

One line per flagged test (§4), a `worth-check: kept:` line per kept test, a
`worth-check: shrinkable:` line per baseline entry that no longer flags, a
`<path>  not checked (<reason>)` line per unread file, then
`worth-check: N flagged (M in baseline), K files read, U not checked (languages: ...)`.
Exit 0: nothing new is flagged, or the plant is not configured. Exit 1: a flagged
test is neither kept nor in the baseline, or `--write-baseline` was refused.
Exit 2: a usage error or an unreadable input. `--json` prints every test read
with its verdict (`flagged`, `spared`, `kept`) and reason.

### Baseline

`docs/graph/worth-baseline.txt` is plant state, tracked in Git and never placed
by the installer: one comment line, then one `path::name` per line. It only
shrinks after the first write.

## 7. Failure modes

### Failure: HEURISTIC_SPARES_A_READ_BACK
- **Trigger:** a read-back test calls a helper the check cannot see into, or
  carries a security or bug word for an unrelated reason
- **Response:** the test is spared; the check errs toward sparing by design
- **Recovery:** a reviewer still applies `test-first.proportionate-checks`

### Failure: ADOPTED_SUITE_FLAGS_ON_DAY_ONE
- **Trigger:** a project adopted with an existing suite holds many read-back
  tests
- **Response:** graft lists them as one judgment item; graft and grow remove
  no test
- **Recovery:** the owner decides per plant to record a baseline, keep tests
  with reasons, or leave them flagged

## 8. Examples

```
$ python3 docs/graph/worth-check.py
tests/test_labels.py::test_submit_label  reads back "Send" that the same file/change adds; only assertion(s): 1; keep it with a line "# worth-check: keep — <reason>" above the test if it earns its place
tests/e2e/smoke.sh  not checked (shell)
worth-check: 1 flagged (0 in baseline), 12 files read, 1 not checked (languages: shell)
worth-check: FAIL — 1 flagged test(s) are not in the baseline. ...
```

## 9. Acceptance criteria

- [x] AC-1: a read-back test in Python, TypeScript or JavaScript is flagged with
  a line that names it, the literal, the assertion count and the keep line;
  maps to WORTH_FLAGS_A_READ_BACK_TEST, WORTH_NEVER_FLAGS_BY_NAME_OR_LENGTH
- [x] AC-2: a logic test, a bug regression and a security negative control are
  never flagged; maps to WORTH_SPARES_LOGIC_TESTS, WORTH_SPARES_BUG_REGRESSIONS,
  WORTH_SPARES_SECURITY_CONTROLS
- [x] AC-3: an unread file is not checked and an unconfigured plant is named,
  never called clean; maps to WORTH_UNREAD_FILE_IS_NOT_CHECKED,
  WORTH_UNCONFIGURED_PLANT_IS_NAMED
- [x] AC-4: a kept test passes with its reason, the baseline holds older flags
  and only shrinks, and a new flag fails; maps to
  WORTH_KEEP_MARKER_KEEPS_WITH_REASON, WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS,
  WORTH_BASELINE_ONLY_SHRINKS
- [x] AC-5: bad input exits 2, no test is edited, and every install places the
  tool; maps to WORTH_BAD_INPUT_EXITS_2, WORTH_NEVER_EDITS_A_TEST,
  WORTH_CHECK_IS_PLACED

## 10. Test mapping

(Owned by `tester`.) Each case runs the placed copy over a temp plant that holds
the fixture suite of `tests/fixtures/worth/` under `tests/`, and the verdict each
fixture test is owed is `tests/fixtures/worth/expected.tsv`, written before the
tool. Every row was `red` on the missing tool first.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| WORTH_FLAGS_A_READ_BACK_TEST | X580 every fixture read-back test is flagged; the Python and TypeScript lines, the summary and the closing line | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SPARES_LOGIC_TESTS | X581 the pattern, condition, precedence, computed-value, written-file and two-homes fixtures are read and spared | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SPARES_BUG_REGRESSIONS | X582 the regression fixtures, one with the read-back shape, are spared | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_SPARES_SECURITY_CONTROLS | X583 the refusal, absence and security-setting fixtures are spared | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_NEVER_FLAGS_BY_NAME_OR_LENGTH | X584 a logic-promising name, six assertions, a shared name and a test with no assertion | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_UNREAD_FILE_IS_NOT_CHECKED | X585 a shell and a Go test, and a Python and a TypeScript file that do not parse | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_UNCONFIGURED_PLANT_IS_NAMED | X586 no spec-lint.py, and one with no TEST_GLOBS, each plain, with --json and with --write-baseline | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_KEEP_MARKER_KEEPS_WITH_REASON | X587 a Python and a TypeScript keep line with a reason, and one without | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_NEW_FLAG_OUTSIDE_BASELINE_FAILS | X588 the first write, a run over the baseline, a new read-back test | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_BASELINE_ONLY_SHRINKS | X589 a refused growth leaves the file; shrinkable reported; the shrink written | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_BAD_INPUT_EXITS_2 | X590 unknown option, missing PATH, a non-UTF-8 file, a partial baseline; a PATH narrows the read | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_NEVER_EDITS_A_TEST | X591 the fixture suite's digest before and after every run | tests/test-worth-check.sh | integration (fixture) | green |
| WORTH_CHECK_IS_PLACED | X592 a fresh install places the seed's file, which answers --help and reads an empty plant | tests/test-worth-check.sh | integration (temp install) | green |
| HEURISTIC_SPARES_A_READ_BACK | none: the check errs toward sparing by design | none | none | none |
| ADOPTED_SUITE_FLAGS_ON_DAY_ONE | none: graft's judgment item is advice, and the owner decides | none | none | none |

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Should an independent tester review the fixture suite? | the fixtures and their verdicts were written by the spawn that built the tool | the verdict table was written before the tool and each case was seen failing first | tester | the round's review |
| Should a later language be read, shell first? | D4 reads Python and TypeScript or JavaScript only | every other language is listed as not checked | owner | a plant that needs it, named by the owner |

## 12. Changelog

- 2026-11-10 — created by `architect` from the round's surface definition of the
  worth check and the owner's decisions of 2026-11-10 (languages read; the
  baseline of a grafted plant decided per plant). Thirteen contracts; the
  fixture suite and its verdict table written first, every case seen failing on
  the missing tool, then green with the tool, the placement and the gate row.
