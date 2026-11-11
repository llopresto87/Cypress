---
status: back-written
status_date: 2026-11-10
owner: architect
status_evidence: tests/test-brief.sh (X570 to X575, X730, X731 and X740 to X748, wired into tests/run.sh through the brief step) and tests/test-worth-check.sh (X603, X604), each case seen failing against the composer without the merged kind and against an effort-scale node without the band line before the code and the line landed; X740 to X747 seen failing against the composer that read an unreadable band, trust claim or §10 origin as a merged path or under another reason, X748 green at its first run and kept as the design-origin control
---

# SPEC-0008: who writes the test

## 0. Metadata

- **Identifier:** SPEC-0008-who-writes-the-test
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-11-10
- **Last reviewed:** 2026-11-11
- **Related grill section:** docs/plans/grill-8.5.0-tester-surfaces.md §9,
  the increment that carries step T9 (to be added by the session)
- **Related ADRs:** adr-0034-a-test-is-owed-only-where-it-can-catch-something
  (OD2, and its amendment of 2026-11-10 on the effort-scale and
  green-self-test sentences)
- **Related specs:** SPEC-0005-cycle-economy (the effort table, the batch
  record and the brief composer's other contracts)
- **Related wiki pages:** none (stdlib Python and POSIX shell only)
- **Design latitude:** narrow. The owner decided on 2026-11-10 that for
  low-risk logic off trust paths the implementer writes the test and the code
  in one spawn, and that the low-risk band is the two lowest effort labels,
  `low` and `medium-low`, recorded as a default the owner can move; the
  owner decided on 2026-11-11 that a bug reproduction owes a tester when it
  arrives as a §10 row of origin `bug` in a spec'd increment, and that a
  contained-lane defect fix keeps one worker writing the reproduction test
  and the fix, the test seen failing before the fix and kept, the reviewer a
  separate spawn
- **Supersedes:** none
- **Superseded by:** none
- **Sign-offs:** product [ ] · architect [ ] · tester [x] · security [ ]
  Back-written on 2026-11-10 by the implementer of step T9 from the owner's
  words, after the RED of X570 to X575 and the code; no promotion was signed.
  The round's architect and tester review it before it is promoted. Tester
  (independent) 2026-11-11: every brief-composer contract and failure mode is
  held by a case that runs the installed composer and watches its exit code,
  refusal line and spawn log; X603 and X604 are text checks, stated as such in
  §11.

## 1. Summary

ADR-0034 OD2 lets one implementer write the test and the code for low-risk
logic off trust paths. This spec holds the reading a tool can take of that
rule. The low-risk band has one home, the `**The low-risk band** is ...` line
of `delegation.effort-scale` in `core/method/delegation-cycle-economy.md`.
`tools/brief.py --role implementer --kind merged --increments N[,N] --unit U`
composes the one implementer brief for such an increment and refuses, naming
the reason, an increment that owes a tester. A tester brief for an increment
inside the band names the merged path to the caller and is composed anyway.

## 2. Scope

In scope: the brief composer's merged kind, the reading of the band, the
trust-path marking, the stateful or concurrent mark, the bug origin of a
§10 row, and who removes a test that catches nothing (ADR-0034 OD3): the
writer's charter and the mutation pass's per-test result. Out of scope: how the orchestrator records the RED of a merged spawn
in the batch record (`delegation.green-self-test` says it records it from the
hand-back), and the prose of the charters and nodes, which the reviewer judges.

## 3. User-facing behavior

The orchestrator composes a brief. For a low-band increment off trust paths
that cites a §10 test, with its own GREEN, it gets one implementer brief whose
task tells the worker to see the test fail for the right reason before any
code and to record both runs. For any other increment that cites a test, the
merged brief is refused with one stderr line that names the increments and
every reason, and a tester brief composes as before.

## 4. Functional contracts

(Authored from the owner's words of 2026-11-10.)

Every contract runs `docs/graph/brief.py` in a fresh claude-code install with
a plan copied from `tests/fixtures/cycle/grill.md` and extended by the case.
"Cites a §10 test" means the increment's `Tests to write (RED)` field does not
start with `none`. A cited RED's own GREEN (an increment whose `Depends on:`
names it and which shares a contract with it) is read with it.

### Contract: LOW_BAND_INCREMENT_COMPOSES_ONE_IMPLEMENTER_BRIEF
- **Given:** a plant that marks a trust path, and a RED increment labelled
  `low` with its own GREEN, neither touching a marked path
- **When:** `brief.py --role implementer --kind merged --increments 1,3 --unit u` runs
- **Then:** it exits 0, prints `effort: low (implementer merged, label low)`,
  and the brief carries a `## One spawn: the test first, then the code`
  section that asks for the test seen failing for the right reason before any
  code and both observations recorded
- **And:** the spawn log record carries `"merged": [1, 3]`
- **And:** `--kind merged` without `--increments` exits 2 naming what it reads

### Contract: TRUST_PATH_INCREMENT_OWES_A_TESTER
- **Given:** a low-band RED whose own GREEN touches a path a `trust: true`
  crosscut claims, or any increment in a plant that marks no trust path
- **When:** the merged brief is composed
- **Then:** it exits 2 with `owe a tester RED spawn: on a trust path (<path>:
  <crosscut>)`, or `the plant marks no trust path, so the doubt is read as one`
- **And:** a tester brief for the same increment composes, exit 0, and names
  no merged path

### Contract: ABOVE_BAND_INCREMENT_OWES_A_TESTER
- **Given:** a RED labelled `medium` with its own GREEN, off trust paths
- **When:** the merged brief is composed
- **Then:** it exits 2 with `label medium is above the low-risk band (low, medium-low)`
- **And:** a tester brief composes, exit 0

### Contract: STATEFUL_CONCURRENT_OR_BUG_REPRODUCTION_OWES_A_TESTER
- **Given:** a low-band RED in a spec'd increment (its `Spec contracts:`
  cites a `SPEC-NNNN/SLUG`) whose contract a §10 risk row of origin `bug`
  covers, or a low-band increment briefed with `--alone <reason>`
- **When:** the merged brief is composed
- **Then:** it exits 2 with `its test reproduces a bug (SPEC-NNNN §10 origin
  bug)`, or `stateful or concurrent (<reason>)`
- **And:** a tester brief composes, exit 0

### Contract: LOW_BAND_IS_READ_FROM_THE_EFFORT_SCALE_NODE
- **Given:** a `medium-low` RED off trust paths, which the default band admits
- **When:** the band line of the installed effort-scale node is changed to
  `low` alone and the merged brief is composed again
- **Then:** the first composition exits 0 and the second exits 2 with
  `label medium-low is above the low-risk band (low)`

### Contract: WRITER_REMOVES_A_TEST_THAT_CATCHES_NOTHING
- **Given:** a test written inside a unit of work that the worth check flags
  or the spec's mutation pass reports `survived-all`
- **When:** the worker that wrote it reads its installed charter
- **Then:** the tester's and the implementer's charters send it to
  `protocol.test-first`, Removing a test that catches nothing, which has the
  class of worker that wrote the test remove it before delivery with
  `removed: <reason>` in its §10 row, lists an older test for the owner's
  confirmation by name, holds back a bug reproduction, a security control and
  a test with no §10 row, and leaves graft and grow removing nothing

### Contract: MUTATION_PASS_REPORTS_EACH_TEST
- **Given:** a spec's end-of-spec mutation pass (`delegation.mutation-at-end`),
  mandatory where it was before and nowhere else
- **When:** the pass hands back its result
- **Then:** the installed node asks for one line per test of the spec it
  covers, `killed <path::name>` or `survived-all <path::name>`, and still
  makes the pass mandatory for security, data-integrity and money contracts
  only

### Contract: CONTAINED_LANE_DEFECT_COMPOSES_ONE_IMPLEMENTER_BRIEF
- **Given:** a plant that marks a trust path, and a low-band increment off
  trust paths whose `Spec contracts:` reads `none` (the contained lane,
  `tiers.contained-lane`), whose title names the defect it reproduces, and
  which cites its reproduction test
- **When:** `brief.py --role implementer --kind merged --increments N --unit u` runs
- **Then:** it exits 0 and the brief asks for the reproduction test seen
  failing for the right reason before any code, and the spawn log record
  carries `"merged": [N]`
- **And:** a tester brief for the same increment names the merged path

### Contract: CONTAINED_LANE_DEFECT_KEEPS_THE_OTHER_REASONS
- **Given:** a contained-lane defect, as above, whose fix touches a path a
  `trust: true` crosscut claims
- **When:** the merged brief is composed
- **Then:** it exits 2 naming `on a trust path (<path>: <crosscut>)`, and the
  line names no bug reproduction among its reasons

### Contract: TESTER_BRIEF_NAMES_THE_MERGED_PATH
- **Given:** a low-band RED off trust paths
- **When:** a tester brief is composed for it
- **Then:** it exits 0 and stderr names the merged path:
  `one implementer spawn writes its test and code (--role implementer --kind merged; tiers.execution-paths)`

### Contract: DESIGN_ORIGIN_ROW_KEEPS_THE_MERGED_BRIEF
- **Given:** a plant that marks a trust path, and a low-band RED off trust
  paths in a spec'd increment whose contract a §10 risk row of origin
  `design` covers
- **When:** the merged brief is composed, then the row's origin is changed to
  `bug` and it is composed again
- **Then:** the first composition exits 0 with the merged brief, and the
  second exits 2 with `its test reproduces a bug (SPEC-NNNN §10 origin bug)`

The next three contracts hold the owner's decision of 2026-11-10 on its safe
side: a reading the composer cannot take is a doubt, and a doubt keeps the
independent tester. Each refusal names what could not be read and what fixes
it, and a tester brief for the same increments composes, exit 0.

### Contract: BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF
- **Given:** a low-band increment off trust paths that composes the merged
  brief, and an installed effort-scale node whose band line is removed, whose
  band line names no label, or which is itself missing
- **When:** the merged brief is composed
- **Then:** it exits 2 with `the low-risk band cannot be read:
  method/delegation-cycle-economy.md <what is wrong>; restore the
  `**The low-risk band** is ...` line (delegation.effort-scale)`
- **And:** with the line restored the same increments compose the merged
  brief again

### Contract: TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF
- **Given:** a low-band increment off trust paths that composes the merged
  brief, and one of: `docs/graph/nodes/` missing; a node whose frontmatter
  does not parse; a node the composer cannot open; a `trust: true` crosscut
  below `nodes/`, where `graph-lint.py` reads no node; `graph-lint.py
  --trust-claims` not answering; an increment whose `Files touched:` names its
  path without backticks, or names no path
- **When:** the merged brief is composed
- **Then:** it exits 2 with `the trust-path claims cannot be read: <what>;
  <the fix>`, and a missing nodes directory is named apart from a plant that
  marks no trust path
- **And:** `Files touched:` is read through `grill-lint.py`'s own path reader,
  so an unquoted path a trust crosscut claims is refused `on a trust path`,
  and an increment naming no path is refused with `increment N names no path
  under Files touched, so its trust path cannot be read; name the files it
  touches`

### Contract: BUG_ORIGINS_UNREADABLE_REFUSES_THE_MERGED_BRIEF
- **Given:** a low-band spec'd RED off trust paths whose §10 rows are of no
  `bug` origin, and `spec-lint.py` missing, or the cited spec unreadable
- **When:** the merged brief is composed
- **Then:** it exits 2 with `the §10 origins cannot be read: <what>; <the fix>`

## 5. Non-functional requirements

Stdlib Python only. The composer reads the plan and its `Files touched:` paths
through `grill-lint.py`'s own field and path readers, the §10 rows through
`spec-lint.py`'s own row reader, the nodes through `frontmatter.py`, and the
trust claims through `graph-lint.py --trust-claims`; a tester brief's notice
never blocks it. Every reading fails closed.

## 6. Data shapes

The band line: `**The low-risk band** is` followed by the backticked labels
before the first `(`. The refusal: `brief: increment[s] N[,N] owe[s] a tester
RED spawn: <reason>[; <reason>]; compose --role tester (delegation.effort-scale)`.
A reading the composer cannot take is a reason of its own: `the low-risk band
cannot be read: ...`, `the trust-path claims cannot be read: ...`, `increment
N names no path under Files touched, ...` or `the §10 origins cannot be read:
...`, each ending in what fixes it.

## 7. Failure modes

### Failure: BAND_LINE_MISSING
- **Trigger:** the effort-scale node is missing or does not open, or has no
  band line, or its band line names no label
- **Result:** every merged brief is refused, naming the band line to restore
  (BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF)

### Failure: TRUST_CLAIMS_UNREADABLE
- **Trigger:** the nodes directory is missing, a node does not open or parse,
  a crosscut sits below `nodes/`, an increment names no path, or
  `graph-lint.py --trust-claims` does not answer
- **Result:** the merged brief is refused, naming what could not be read and
  what fixes it (TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF)

### Failure: BUG_ORIGINS_UNREADABLE
- **Trigger:** `spec-lint.py` does not load, or a cited spec does not open
- **Result:** the merged brief is refused, naming what to restore
  (BUG_ORIGINS_UNREADABLE_REFUSES_THE_MERGED_BRIEF)

## 8. Examples

`brief.py --role implementer --kind merged --increments 5,6 --unit u` on a
`medium` increment prints
`brief: increments 5,6 owe a tester RED spawn: label medium is above the
low-risk band (low, medium-low); compose --role tester (delegation.effort-scale)`.

## 9. Acceptance criteria

- [x] AC-1: a low-band increment off trust paths composes one implementer
  brief, RED first; maps to LOW_BAND_INCREMENT_COMPOSES_ONE_IMPLEMENTER_BRIEF,
  TESTER_BRIEF_NAMES_THE_MERGED_PATH
- [x] AC-2: a trust path, a label above the band, stateful or concurrent code
  and a spec'd increment's bug reproduction keep a tester; maps to TRUST_PATH_INCREMENT_OWES_A_TESTER,
  ABOVE_BAND_INCREMENT_OWES_A_TESTER,
  STATEFUL_CONCURRENT_OR_BUG_REPRODUCTION_OWES_A_TESTER
- [x] AC-3: the band has one home the owner can move; maps to
  LOW_BAND_IS_READ_FROM_THE_EFFORT_SCALE_NODE
- [x] AC-4: the worker that wrote a test that catches nothing removes it, and
  the mutation pass names each test it killed nothing with; maps to
  WRITER_REMOVES_A_TEST_THAT_CATCHES_NOTHING, MUTATION_PASS_REPORTS_EACH_TEST
- [x] AC-5: a contained-lane defect fix keeps one worker for its
  reproduction test and its fix, and every other reason still owes a
  tester; maps to
  CONTAINED_LANE_DEFECT_COMPOSES_ONE_IMPLEMENTER_BRIEF,
  CONTAINED_LANE_DEFECT_KEEPS_THE_OTHER_REASONS
- [x] AC-6: a reading the composer cannot take keeps the tester, and only a
  §10 row of origin `bug` counts as a bug reproduction; maps to
  BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF,
  TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF,
  BUG_ORIGINS_UNREADABLE_REFUSES_THE_MERGED_BRIEF,
  DESIGN_ORIGIN_ROW_KEEPS_THE_MERGED_BRIEF

## 10. Test mapping

Each case carries its label and the slug it asserts in its `ok`/`bad` line.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| LOW_BAND_INCREMENT_COMPOSES_ONE_IMPLEMENTER_BRIEF | X570 merged brief composed and logged; no increments refused | tests/test-brief.sh | integration (fresh install) | green |
| TRUST_PATH_INCREMENT_OWES_A_TESTER | X571 unmarked plant, marked trust path, tester brief composes | tests/test-brief.sh | integration (fresh install) | green |
| ABOVE_BAND_INCREMENT_OWES_A_TESTER | X572 a medium increment | tests/test-brief.sh | integration (fresh install) | green |
| STATEFUL_CONCURRENT_OR_BUG_REPRODUCTION_OWES_A_TESTER | X573 a bug-origin §10 row; `--alone` | tests/test-brief.sh | integration (fresh install) | green |
| LOW_BAND_IS_READ_FROM_THE_EFFORT_SCALE_NODE | X574 the band line moved in the installed node | tests/test-brief.sh | integration (fresh install) | green |
| CONTAINED_LANE_DEFECT_COMPOSES_ONE_IMPLEMENTER_BRIEF | X730 a contained-lane defect: merged brief composed and logged; the tester notice | tests/test-brief.sh | integration (fresh install) | green |
| CONTAINED_LANE_DEFECT_KEEPS_THE_OTHER_REASONS | X731 a contained-lane defect on a trust path | tests/test-brief.sh | integration (fresh install) | green |
| TESTER_BRIEF_NAMES_THE_MERGED_PATH | X575 the notice on a tester brief | tests/test-brief.sh | integration (fresh install) | green |
| WRITER_REMOVES_A_TEST_THAT_CATCHES_NOTHING | X603 the installed charters' pointer resolves to a section holding each removal rule | tests/test-worth-check.sh | integration (fresh install) | green |
| MUTATION_PASS_REPORTS_EACH_TEST | X604 the installed mutation-at-end section: a line per test, mandatory classes unchanged | tests/test-worth-check.sh | integration (fresh install) | green |
| DESIGN_ORIGIN_ROW_KEEPS_THE_MERGED_BRIEF | X748 a design-origin §10 row composes; the same row of origin bug owes a tester | tests/test-brief.sh | integration (fresh install) | green |
| BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF | X740 band line removed, naming no label, node missing; restored band composes | tests/test-brief.sh | integration (fresh install) | green |
| TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF | X741 the nodes directory missing | tests/test-brief.sh | integration (fresh install) | green |
| TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF | X742 a node with unterminated frontmatter | tests/test-brief.sh | integration (fresh install) | green |
| TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF | X743 a node the composer cannot open (skipped where the user reads a mode-000 file) | tests/test-brief.sh | integration (fresh install) | green |
| TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF | X744 a trust crosscut below nodes/ | tests/test-brief.sh | integration (fresh install) | green |
| TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF | X745 graph-lint.py --trust-claims not answering | tests/test-brief.sh | integration (fresh install) | green |
| TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF | X746 an unquoted trust path; an increment naming no path | tests/test-brief.sh | integration (fresh install) | green |
| BUG_ORIGINS_UNREADABLE_REFUSES_THE_MERGED_BRIEF | X747 spec-lint.py missing; the cited spec unreadable | tests/test-brief.sh | integration (fresh install) | green |
| BAND_LINE_MISSING | X740 (BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF) | tests/test-brief.sh | integration (fresh install) | green |
| TRUST_CLAIMS_UNREADABLE | X741 to X746 (TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF) | tests/test-brief.sh | integration (fresh install) | green |
| BUG_ORIGINS_UNREADABLE | X747 (BUG_ORIGINS_UNREADABLE_REFUSES_THE_MERGED_BRIEF) | tests/test-brief.sh | integration (fresh install) | green |

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Should `cycle.py` record a merged spawn's RED from its hand-back by itself? | the batch record's hashes are written when the orchestrator observes a RED | the orchestrator records it from the hand-back with `cycle.py record-red` | architect | a later round |
| Should WRITER_REMOVES_A_TEST_THAT_CATCHES_NOTHING and MUTATION_PASS_REPORTS_EACH_TEST carry `Check: review`? | the seed's documentation is its product, so a text check that keeps a rule in the installed nodes holds something; it does not observe a worker removing a test or a pass reporting one | X603's pointer-to-heading arm checks something real: each installed charter's pointer resolves to a section of the installed protocol holding every removal rule, two homes held equal, and a renamed heading or a dropped rule turns it red. The removal itself is a worker's act, judgment in ADR-0003's classes (the writer in its unit of work, the owner for an older test), and no tool composes or observes it. X604 is a documentation rule held by a text check: soft in ADR-0003's classes for the installed node carrying the per-test report line and the mandatory classes, in the seed's own gate only; the report itself is judgment (the worker running the pass, then the orchestrator reading its hand-back), and no test of it can exist while no tool runs the pass. Both stay kind `test` as text checks, stated as such | architect | a tool that runs the mutation pass or records a removal, which would give each a behavioural case |
| Should a cited spec that is not in `specs/` refuse the merged brief? | its §10 origins cannot be read, so a bug row there is unseen; the composer reads only the specs it finds | a missing spec is the spec and plan lints' finding, and the composer reads what is present | architect | a later round, with the cycle fixture given its spec |

## 12. Changelog

- 2026-11-10 — created `back-written` from the owner's words of 2026-11-10
  (ADR-0034 OD2, decision D1 option a) with the RED of X570 to X575 in
  `tests/test-brief.sh`, each seen failing first; six contracts, unsigned.
- 2026-11-10 — two contracts added by the implementer of step T11 (ADR-0034
  OD3): WRITER_REMOVES_A_TEST_THAT_CATCHES_NOTHING and
  MUTATION_PASS_REPORTS_EACH_TEST, with X603 and X604 in
  `tests/test-worth-check.sh`, each seen failing against the charters and
  nodes without the text, then green.
- 2026-11-11 — the owner decided on 2026-11-11 that a bug reproduction owes a
  tester only in a spec'd increment and that a contained-lane defect fix keeps
  one worker: STATEFUL_CONCURRENT_OR_BUG_REPRODUCTION_OWES_A_TESTER scoped to
  spec'd increments, and CONTAINED_LANE_DEFECT_COMPOSES_ONE_IMPLEMENTER_BRIEF
  and CONTAINED_LANE_DEFECT_KEEPS_THE_OTHER_REASONS added with X730 and X731
  in `tests/test-brief.sh`, both seen failing against the composer that read
  a contained-lane title naming a reproduction as a bug, then green.
- 2026-11-11 — an independent tester read each contract and each cited case
  (X570 to X575, X730 and X731 in `tests/test-brief.sh`; X603 and X604 in
  `tests/test-worth-check.sh`). The eight brief-composer contracts are
  observable and their cases watch exit codes, refusal lines and the spawn
  log. X603 and X604 read back the sentences the same change added, and the
  two failure modes have no case; the tester sign is withheld and the
  findings are in §11.
- 2026-11-11 — the tester's findings closed. Cases X740 to X747 in
  `tests/test-brief.sh` were written first: X744 (a trust crosscut below
  `nodes/`), X746 (an unquoted trust path, and an increment naming no path)
  and X747 (`spec-lint.py` missing) found the composer failing open into a
  merged brief; X740 to X743, X745 and the unreadable spec of X747 found it
  refusing under a reason that named the wrong thing or no fix. The composer
  now fails closed with a reason naming what could not be read and what fixes
  it: BAND_UNREADABLE_REFUSES_THE_MERGED_BRIEF,
  TRUST_CLAIMS_UNREADABLE_REFUSES_THE_MERGED_BRIEF and
  BUG_ORIGINS_UNREADABLE_REFUSES_THE_MERGED_BRIEF added, the failure modes
  mapped to them, and BUG_ORIGINS_UNREADABLE added. X748
  (DESIGN_ORIGIN_ROW_KEEPS_THE_MERGED_BRIEF) was green at its first run and
  stays as X573's design-origin control. §11 states what X603 and X604 hold
  and their ADR-0003 classes; the tester sign is still the round's to give.
- 2026-11-11 — the independent tester re-reviewed X740 to X748 and signed as
  tester in §0. Each fail-closed case breaks one reading in a fresh install
  (the band line, the nodes directory, a node, `graph-lint.py`, the path
  reader, `spec-lint.py`, a spec), sees the merged brief refused with the
  reading and its fix named, sees the tester brief compose, and restores the
  reading; X740 sees the restored band compose again, and X748 holds the
  design-origin control X573 lacked. The tester accepts the classification
  of X603 and X604 as text checks of documentation rules (ADR-0003 soft for
  the installed text, judgment for the act), stated in §11, and accepts the
  cited-spec-missing path as documented there with the plan lint's finding
  behind it. Two mode-000 arms (X743, the unreadable spec of X747) are
  skipped where the user reads such a file, and X747's skip prints no line.
