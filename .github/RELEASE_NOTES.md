## 8.5.0 — a test is owed only where it can catch something (2026-11-10)

The seed already held that a test which only proves a change is present is not
worth writing (`test-first.proportionate-checks`). The roles that decide
whether a test exists never loaded that rule: after an install, the
architect's, the tester's and the reviewer's prompts carried none of its
sentences, and the tester's charter said every increment begins with a failing
test named after its contract. The gates asked for the same thing. The spec lint
wanted a test naming every live contract, the plan lint kept a test on any row
the planner could not call, and the implementer stopped when no failing test
existed. A worker that followed the text it loaded wrote the pointless test.

The owner decided on 2026-11-10 that the architect sets how each contract is
checked (`test`, `run`, `review` or `covered`) and the tester can challenge it;
that one implementer writes the test and the code for low-risk logic off trust
paths; that a test which catches nothing is removed, by the worker inside the
unit of work that wrote it and otherwise in a batch the owner confirms; that
graft and grow remove no test; and that these amend in part the decision of
2026-11-02 (tests are planned before they are written, not deduped after) and
the rule that a RED writer adds, merges or drops no case, which now allows
dropping and merging
([ADR-0034](docs/decisions/adr-0034-a-test-is-owed-only-where-it-can-catch-something.md)).
The owner answered the round's five open questions the same day: the low-risk
band is the two lowest effort labels, `low` and `medium-low`; in a spec of the
new form the §10 Covers cell links a test to its contracts, and the contract's
name in test code no longer does; the seed's own specs stay in the earlier form
and a later round labels single contracts; the worth check reads Python and
TypeScript or JavaScript; and a grafted plant's baseline only shrinks, with its
tests listed for the owner's confirmation when their spec is reopened
(clean as you touch). The notes are in
`docs/plans/owner-decisions-8.5.0-tester-surfaces.md`.

The owner decided three more findings on 2026-11-11, before the release: how a
re-install treats a plant's edited host settings, which agents the lead may
launch on opencode, and what an unknown tool name in a plant's agent does to the
opencode install. The same day the owner scoped who writes a bug's
reproduction, and ruled that a plant need blocks a fresh growth but not a
graft. The sections below describe the release as decided.

The kernel is 7043 bytes. The always-loaded surface on Claude Code and opencode
is 67065 bytes, against 67131 in 8.4.0; no budget moved. The composed prompts
are 41589 bytes for the architect, 42960 for the tester, 47914 for the
reviewer, 44845 for the orchestrator and 58991 for the implementer.

### The rule reaches the roles that decide

- **It is the first section of `skill.test-first`**, and the architect, the
  tester and the reviewer load it through `always_loads:` by slug. The agent
  composer now accepts a slug there and carries that one section.
- **The tester's description reads "Writes failing tests for logic
  contracts"**, so the router sends it the contracts that owe a test.
- **The lead carries a two-line pointer** to the rule. The architect slices the
  plan from the kinds it set at specify, so the lead does not need the rule
  itself. The routing hints and examples that an earlier draft of the round
  removed from the lead's charter are back.
- **A lint holds the delivery.** `tools/delivery_rules.py` keeps one table of
  the rules that must reach a role and the sentence that proves each one is
  present. The seed lint runs it over the composed agents, and
  `install.sh --check` runs it over a plant's `.claude/agents` and
  `.opencode/agents`, naming each role whose loaded prompt lacks a rule.
  It is a seed-side tool, run from the seed and placed in no plant.

### The gates ask for what the rule asks

- **Each contract has a kind.** A spec in the new form gives every §4 contract
  a `Check:` line. `test` is logic that can be wrong while the code is present,
  covered by a §10 row. `run` is a declarative change proved by a named command
  and its result. `review` is wording or presentation, confirmed by a reviewer
  spawn. `covered` names the existing test that already asserts it. When the
  architect cannot tell, the kind is `test`. A `Challenge` line records the
  tester's challenge and the architect's answer, and a kind the architect keeps
  against it goes to the owner before sign-off.
- **Declared values have a table of their own.** A label, a route, a flag or a
  key with nothing to get wrong is a row of §4's declared-values table, proved
  whole by one run or review, and is not a contract.
- **§10 is a risk-based test design.** The tester writes it once, after
  surveying the existing suite: one row per risk (what breaks, for whom), its
  lowest-level test, the contracts it covers, and its origin (`design`, `bug`
  or `security control`). A spec with no `test` or `covered` contract and no
  trust path gets no test-design spawn and no tester sign-off.
- **The spec lint reads evidence by kind** (SPEC-0008): a §10 Covers cell
  citing a test the suite holds, a recorded command and result, a reviewer's
  confirmation, or the existing test. A row marked `removed:` covers nothing.
- **The plan lint holds the increment fields to the kinds.** An increment cites
  the §10 rows of its `test` contracts, carries a `Run:` or `Review:` field for
  the others, and schedules no RED spawn when it holds no `test` contract.
- **The implementer starts from the evidence its contracts declare**: a failing
  test for each `test` contract, the plan's `Run:` or `Review:` for the others.
  With neither, it hands back naming the tester or the architect. The reviewer's
  first review checks that code under a `run` or `review` contract holds no logic.
- **Low-risk increments take the merged path.** An increment labelled `low` or
  `medium-low`, off trust paths, not stateful or concurrent and not a bug
  reproduction in a spec'd increment, goes to one implementer
  (`brief.py --kind merged`). It sees the test fail for the right reason, then
  writes the code, and its hand-back records both runs. Everything else keeps a
  separate tester RED. The composer fails closed: when it cannot read the
  band line of `delegation.effort-scale`, the plant's trust-path claims or the
  spec's §10 origins, it refuses the merged brief, names what it could not read
  and the fix, and the increment goes to a tester. An independent review found
  three readings that let a merged brief through, and this release closes them.
- **A bug reproduction owes a tester only in a spec'd increment**, one whose
  §10 row has origin `bug`. The owner decided on 2026-11-11 that a defect fix
  on the contained lane stays with one worker: the implementer writes the
  reproduction test, sees it fail before the fix, then fixes, and the test
  stays; the reviewer is a separate spawn. The composer no longer asks for a
  tester on a contained-lane defect because its title says bug.
- **A RED writer may drop or merge a designed case** that, on contact with the
  code, only reads back a value or duplicates another, with one line of reason
  in its §10 row. Only the design adds a case.
- **The worth check** (`docs/graph/worth-check.py`, placed in every plant,
  SPEC-0009) flags a test whose only assertions read back a literal the same
  change adds. It spares a test that feeds inputs to logic, a bug regression and
  a security negative control, honours a `worth-check: keep — <reason>` line, and
  reads Python and TypeScript or JavaScript; every other test file is listed as
  not checked. Older flags live in the plant's `docs/graph/worth-baseline.txt`,
  which only shrinks. The check never edits a test.
- **The worth check was reworked after an independent tester's review**, on
  2026-11-11:
  - A file that a setup hook's code writes counts as that code's output, so a
    test that reads it is spared. An imported TypeScript or JavaScript name
    counts as code under test.
  - A parametrized test (pytest `parametrize`, `test.each`, `it.each`) is read
    with each parameter's literal values. One whose table it cannot read is
    listed as `not checked (parametrized)`, and a computed title as
    `not checked (computed title)`. Both count in the not-checked figure, and
    the summary ends `(languages: ...; parametrized: N test(s))`.
  - The regression and security spares read the test's name, decorators,
    markers, comments and identifiers. Words inside string literals, colour
    codes and URLs count for neither.
  - A bare boolean compared for equality (`is False`, `toBe(false)`) is a
    read-back. A guard such as `!= ""`, `is not None` or a truthiness check
    spares a test only when it is the test's only kind of assertion. A
    `"".join` over literals and an inline snapshot are folded to their literal
    and flagged.
  - Five read-backs stay spared, as documented limits: an assertion inside a
    helper, a constant held equal to a golden file, a snapshot fixture,
    `toMatchSnapshot`, and a test whose name only claims to be a regression.
    One limit can flag a good test: a setup file named only in the runner's
    configuration is not read, and its author keeps the test with a keep line
    naming that file.
- **Removal follows the owner's rules.** A test that catches nothing (flagged by
  the worth check, or `survived-all` in the spec's mutation pass) is removed by
  the worker that wrote it, inside that unit of work. An older one stays until
  the owner confirms it by name; `worth-check.py --removal-list` prints the
  numbered batch, and `--spec SPEC-NNNN` the batch a reopened spec owes. A bug
  regression, a security control and a test no §10 row maps each wait for a
  decision of their own.
- **Session metrics count tests.** The deliver entry takes five optional
  count lines: tests written by origin, dropped at RED, refused by the worth
  check, removed, and not checked by the worth check (the `U not checked` of
  its summary). An entry without them passes as before.

### A spec shape change: what graft reads as the migration

A spec may now declare `- **Contract form:** kinds` and
`- **Trust path:** yes|no` in its §0. Each contract then says how it is checked,
on its `Check:` line. A spec in the earlier form lints unchanged: a contract
with no `Check:` line is read as `test`, linked by its §10 row and its name in
test code, and a spec in the earlier form may also label single contracts with
`Check:`. Plans in today's form keep linting, `none — <why>; proved by <run>`
included.

A plant converts a spec only as a shape migration. Graft proposes it, when the
spec is reopened or the worth check flags its tests, and the steward ratifies it
in the graft record. `tools/spec-convert.py --dry-run <spec>`, run from the seed,
shows the mechanical part: the two §0 lines and `Check: test` on each unlabelled
contract, with each contract's present mapping (SPEC-0010).
`--write --steward-ratified <spec>` writes only that part, keeps the spec as it
was in a timestamped backup, and leaves every contract `test`. Re-labelling a
contract `run`, `review` or `covered`, the declared values, the risk-based §10
and a trust path set to `yes` are the judgment of the plant's architect. A
converted spec keeps its earlier §10 link until it has a risk table. The tool is
seed-side, like the other graft tools.

### What a graft needs to know

- The changed `spec-lint.py` and `grill-lint.py` engines reach a plant only
  through graft's engine reconciliation, which keeps the plant's `TEST_GLOBS`
  and `SKIP_DIRS`.
- The graft that brings the worth check to a plant records the baseline once,
  with `worth-check.py --write-baseline`, and removes no test.
- Phase 5 now prints a `PLANT NEED` row for each fact a landed capability reads
  from the plant (SPEC-0011): gate output, cache lifetime and the model map, the
  token reader, trust paths, the test layout, and each language's testing idiom
  (`<slug>.testing-idiom` in its expertise node). The owner decided on
  2026-11-11 how they gate. A fresh growth fails on an open need
  (`UNGROWN plant need <id>`, and `HOLLOW` for a missing testing idiom) until
  the plant supplies it or the owner declines it. After a graft each is a
  `note:` line only: Phase 5 and `tools/graft-run.py` pass
  `growth-audit.py --after-graft`, and the delivery lists each one under
  "Grafted but not yet grown". No need blocks daily work; until it is grown
  its capability reports that it is not configured. The coverage rows that
  predate the needs (collections, agents, experts, inventory) still block
  after a graft as before, an open question in SPEC-0011 §11. `models.md` is
  the plant's own file, so copy the seed template's new billing section into
  it and fill it.
- The cycle driver reads the seed's template engine when a plant's
  `grill-lint.py` predates it, and names the engine it used; a plan whose §9
  holds no increments is refused with a line that says so.
- `install.sh --check` names a missing must-reach rule on Claude Code and on
  opencode. It says plainly when an older wiring, which runs a guard with no
  existence test, blocks the tool because the script is missing. For an
  `opencode.json` in the earlier shape it names both remedies, a re-install
  outside a graft and the reconciliation inside one.
- A plain re-install replaces seed-owned charters and host settings and keeps
  each earlier file as a timestamped backup; graft keeps an edited file instead.

### The installer decisions of 2026-11-11

An earlier draft of this entry listed three findings, D6 to D8, as open. The
owner decided all three on 2026-11-11, and this release implements them
(SPEC-0001; the notes are in
`docs/plans/owner-decisions-8.5.0-tester-surfaces.md`).

- **Edited host settings upgrade by graft (D6).** A plain re-install still
  replaces a plant-edited `.claude/settings.json` or `opencode.json` and keeps
  the earlier file as a timestamped backup. It now names each key path the
  plant's file had and the new one lacks, with the backup that holds it, and
  says that edited host settings upgrade by graft, which keeps the edited
  file. A merge on re-install, where the plant owns its keys and the seed adds
  its own, is recorded for a later round with its own spec.
- **The lead's launch list on opencode follows the plant's roster (D7).** The
  installer generates the lead's `subagent` allow list from the roster: the
  seed roster as the lead's charter names it, then each plant agent that passes
  the agent lint. It prints the added agents on one line and leaves a
  lint-dirty plant agent off with a named warning. `install.sh opencode
  --check` reports a list that differs from the roster, with the remedy
  `--recompose-agents`.
- **An unknown tool in a plant's agent is denied, not fatal (D8).** When a
  plant agent's `tools:` names a tool the opencode permission table lacks, that
  tool is denied, a warning names the file and the tool with the remedy (remove
  it from the charter, or the seed adds it to the table), and every agent
  installs. `install.sh opencode --check` fails until it is fixed. A seed
  charter with an unknown tool still stops the run, and a new check in
  `tests/seed-lint.py` (`check_opencode_tool_table`) fails the seed's gate on
  one.

### Not measured

This round did not measure the effect on the tests plants write or the tokens
they spend. The session-metrics counts above are where a later reading starts;
the owner can read this round's own counts in its session records.
