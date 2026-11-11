---
status: back-written
status_date: 2026-11-10
owner: architect
status_evidence: tests/test-growth-audit.sh (X665 to X671, X720 to X724) and tests/test-cycle.sh (X663, X664), wired into tests/run.sh through their existing steps; every case was seen failing first against the tools without the change (no PLANT NEED line, no testing-idiom finding, the old model-map byte comparison, an empty cycle printed with exit 0, a refusal at the first older engine), then green
---

# SPEC-0011: grown, not carried

## 0. Metadata

- **Identifier:** SPEC-0011-grown-not-carried
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-11-10
- **Last reviewed:** 2026-11-11
- **Related grill section:** docs/plans/grill-8.5.0-tester-surfaces.md, the
  requirements that carry the earlier rounds through to plants (F3, F4)
- **Related ADRs:** adr-0022-the-plant-model-map (an unfilled map means
  inherit, disclosed and passed); adr-0034-a-test-is-owed-only-where-it-can-catch-something
  (the trust-path reading and the testing idiom a tester writes against);
  adr-0003-enforcement-layering-honesty (a need is soft in a fresh growth,
  where the coverage gate fails on it, and detective after a graft)
- **Related specs:** SPEC-0005-cycle-economy (the cycle driver, the token
  ledger, the model classes); SPEC-0006-session-metrics (the `Tokens` line
  that may read `not recorded`); SPEC-0008-who-writes-the-test (the
  trust-path reading); SPEC-0009-worth-check (the same `TEST_GLOBS`)
- **Related wiki pages:** none (stdlib Python only)
- **Design latitude:** balanced. The owner decided on 2026-11-11 that an open
  need fails the coverage gate of a fresh growth until it is supplied or
  honestly declined, is a note after a graft, and blocks no daily work,
  because every capability it serves keeps a safe default; it is never
  reported clean
- **Supersedes:** none
- **Superseded by:** none
- **Sign-offs:** product [ ] · architect [ ] · tester [x]
  Back-written on 2026-11-10 by the implementer of the round's F3 and F4
  work, after each case was seen red and then green; no promotion was signed.
  The round's architect and tester review it before it is promoted. Tester
  (independent) 2026-11-11: each contract is held by a case that runs the
  audit, a graft rehearsal or the cycle driver and watches exit codes,
  records and lines.

## 1. Summary

A capability the seed installs is carried into a plant; it is grown only when
the plant supplies the fact the capability reads. The cycle driver needs a
plan with §9 increments and an engine that reads them; the gate-output and
slow-command rules need the plant's own gate commands written to report
failures plainly; the model classes need a model map and, on Claude Code, a
cache lifetime chosen for the plant's billing; the token ledger needs a host
that reports usage; the merged test-and-code spawn needs the plant's trust
paths marked; the worth check and the spec lint need the plant's test layout;
a tester needs the stack's testing idiom. `tools/growth-audit.py` makes each
of these visible as a plant need: `--plan` owes a row for it, the lint names
it while it is not configured, and it closes when the plant supplies it. In a
fresh growth an open need fails the coverage gate; after a graft it is a note
the graft's report lists under "Grafted but not yet grown"; no tool a plant
runs day to day reads one.

## 2. Scope

In scope: the `needs` rows of `.cypress/coverage.json`, the probes that answer
them, their lines in `--plan` and the lint, the testing-idiom finding on a
language's expertise node, where each blocks (a fresh growth, after a graft,
day to day), and the cycle driver's two unconfigured states.

Out of scope: any change to what a capability does when its fact is absent
(each keeps its safe default); the opencode lead's launch list for a plant's
own expert, and an unknown tool name in a plant's agent, which wait on the
owner (`docs/plans/owner-decisions-8.5.0-tester-surfaces.md`).

## 3. User-facing behavior

`growth-audit.py <plant> <seed> --plan` prints, beside its other prompts,
`PLANT NEED   <id> — not configured for this plant: <what is missing>. Supply
<what> (grow.plant-needs), or record the owner's decision to go without in
this row; the coverage gate fails until then` for each open need (with
`--after-graft`: `; until then the graft lists it under "Grafted but not yet
grown" with its reason`), and writes one `needs` row per need the plant owes.

In a fresh growth (no option) the lint reports each open need as
`UNGROWN      plant need <id>` with `not configured for this plant — <what is
missing>. Supply <what> (grow.plant-needs), or record the owner's decision to
go without in this need's row of .cypress/coverage.json: `status: ABSENT` with
the owner's reason`, and exits 1. After a graft (`--after-graft`) it prints
`note: plant need <id> is not configured for this plant — <what is missing>`
instead, a language's missing testing idiom among them as
`<slug>.testing-idiom`, and a passing run ends `coverage complete; <n> plant
need(s) not configured for this plant: <ids>`; the exit code is the verdicts'
alone. A declined need is a note in both modes.

With no token-ledger record, `brief.py --log` prints
`- Tokens: not recorded: no spawn has a record in the token ledger tokens.jsonl`
(observed on 2026-11-10 in a fresh opencode plant); the `token-ledger` need
names that this is the state of every spawn on a host other than Claude Code
until the plant records where the host reports usage.

`docs/graph/cycle.py --unit U` over a plan whose §9 holds no increments
prints one stderr line naming the plan and exits 2. Over a plant whose own
`grill-lint.py` predates it, it reads the plan through the seed template placed
under `docs/graph/templates/knowledge-graph/` and says so on an `engine:` line.

## 4. Functional contracts

### Contract: PLAN_OWES_A_ROW_PER_PLANT_NEED
- **Given:** an installed plant and the seed's `NEEDS` table
- **When:** `growth-audit.py <plant> <seed> --plan` runs
- **Then:** `.cypress/coverage.json` carries one `needs` row per need the
  plant owes (`name`, `what`, `configured`, `detail`, `status`, `reason`), and
  each open need is printed as `PLANT NEED   <id> — not configured for this
  plant: <detail>`
- **And:** a need the plant's hosts do not owe (`cache-lifetime` without
  Claude Code, `token-ledger` with Claude Code alone) has no row, and a need
  already met is a row with `configured: true` and no line

### Contract: UNCONFIGURED_NEED_IS_NAMED_AND_NEVER_BLOCKS
- **Given:** a plant whose every coverage row passes and whose needs are open
- **When:** the lint runs after a graft (`--after-graft`)
- **Then:** it exits 0, prints `note: plant need <id> is not configured for
  this plant — <detail>` per open need, and its last line lists the open
  needs after `coverage complete;`, so no output reads clean
- **And:** the template's verification runbook, still holding its `<gate>`
  row, is named as not configured

### Contract: NEED_CLOSES_WHEN_THE_PLANT_SUPPLIES_IT
- **Given:** the open needs of a claude-code plant
- **When:** the plant writes its gates into `runbooks/verification.md`, fills
  the map and the billing and cache-lifetime lines of `docs/graph/models.md`,
  marks a crosscut `trust: true` and sets `TEST_GLOBS`, then re-plans
- **Then:** `--plan` prints no `PLANT NEED` line, every row is
  `configured: true`, and the lint prints no need and ends `coverage complete`

### Contract: OWNER_DECLINED_NEED_IS_CARRIED_AS_NOT_CONFIGURED
- **Given:** a need's row with `status: ABSENT` and the owner's words in
  `reason`
- **When:** the lint runs, in a fresh growth or after a graft, and `--plan`
  runs again
- **Then:** the lint prints `note: plant need <id> is not configured for this
  plant, by the owner's decision: <reason>`, lists it as `<id> (declined)` on
  its summary line, and its exit code is the verdicts'; `--plan` keeps the
  status and the reason

### Contract: MODEL_MAP_NEED_READS_THE_CELLS_NOT_THE_BYTES
- **Given:** a `docs/graph/models.md` copied from an earlier seed's template
  and never edited (its text differs from today's template; every map cell
  still holds its placeholder)
- **When:** the lint runs after a graft
- **Then:** it prints `note: plant need model-map is not configured for this
  plant — docs/graph/models.md is unfilled, so every agent runs on its
  caller's model`, as it does for today's untouched template, and names the
  missing billing and cache-lifetime section under `cache-lifetime`

### Contract: HOST_NEEDS_FOLLOW_THE_STAMPED_HOSTS
- **Given:** a plant whose needs are all met, then stamped
  `tools: "claude-code opencode"`, with one opencode map cell back at its
  placeholder and a `grill-lint.py` with no `plan_graph`
- **When:** `--plan` runs
- **Then:** it owes `token-ledger` (no `Token usage:` reader recorded for
  opencode, so the `Tokens` line reads `not recorded` there), `model-map`
  (`its opencode column holds the placeholder in 1 of 5 rows`) and
  `cycle-driver` (the engine predates `docs/graph/cycle.py`)

### Contract: LANGUAGE_EXPERTISE_OWNS_ITS_TESTING_IDIOM
- **Given:** an inventory row of kind `language` (not incidental) whose
  `nodes/expertise.<slug>.md` exists
- **When:** `--plan` and the lint run
- **Then:** until the node's `owns:` lists `<slug>.testing-idiom`, `--plan`
  prints `NEEDS TESTING IDIOM language <name>` and the lint reports `HOLLOW`
  naming the missing key; once it does, neither appears
- **And:** a node of another kind is not held to it

### Contract: OPEN_NEED_BLOCKS_A_FRESH_GROWTH
- **Given:** a plant whose every coverage row passes and whose needs are open,
  none declined
- **When:** the lint runs with no option, as a fresh growth runs it
- **Then:** each open need is a failing verdict `UNGROWN      plant need <id>`
  naming what is missing, what satisfies it (`Supply <what>`), and the honest
  decline (`status: ABSENT` with the owner's reason, in the need's row), and
  the lint exits 1
- **And:** once the owner declines each one, the lint exits 0 and carries
  each as a note with its reason

### Contract: PLAN_SAYS_WHERE_AN_OPEN_NEED_GOES
- **Given:** a plant with an open need
- **When:** `--plan` runs, then `--plan --after-graft`
- **Then:** the first `PLANT NEED` line ends `the coverage gate fails until
  then`; the second ends `until then the graft lists it under "Grafted but not
  yet grown" with its reason`

### Contract: TESTING_IDIOM_IS_A_NOTE_AFTER_A_GRAFT
- **Given:** a `language` row whose expertise node owns no `<slug>.testing-idiom`
- **When:** the lint runs with `--after-graft`
- **Then:** it prints `note: plant need <slug>.testing-idiom is not configured
  for this plant — <the gap>`, reports no `HOLLOW` for it, and exits as it
  does once the node owns the key; without the option the `HOLLOW` stands

### Contract: GRAFT_AUDITS_AS_AFTER_A_GRAFT
- **Given:** a plant whose every coverage row passes and whose needs are open,
  none declined, committed to Git
- **When:** `tools/graft-run.py` rehearses a graft of it into a stage
- **Then:** the coverage log of the rehearsal carries each open need as a
  `note: plant need <id> is not configured for this plant` line and no
  `UNGROWN      plant need` verdict, and the gate table's
  `graft.gate.coverage` row is `PASS`
- **And:** the stage copy the rehearsal leaves, audited with no option as a
  fresh growth, fails with `UNGROWN      plant need <id>`; and a reader
  following `protocols/graft.md` Phase 5 and `graft.gate.coverage` runs
  `growth-audit.py` with `--after-graft`, `--plan` and the lint alike (prose,
  held by review and by a text check)

### Contract: NEED_BLOCKS_NO_DAILY_WORK
- **Given:** a plant fresh from `install.sh`
- **When:** its placed tools and hooks are read
- **Then:** `growth-audit.py` is not among them, and the only placed code that
  names `.cypress/coverage.json` is `graph-lint.py` (the plant's and its
  template copy), which reads whether the record exists and no `needs` key

### Contract: CYCLE_DRIVER_NAMES_A_PLAN_WITHOUT_INCREMENTS
- **Given:** a plan whose §9 holds no increment, as a fresh plant's template
  plan does
- **When:** `cycle.py --unit U` runs
- **Then:** it prints nothing on stdout, one stderr line
  `cycle: <plan>: §9 holds no increments, so there is no cycle to drive; write the plan's §9 (protocol.grill), or name the plan that has one with --plan`,
  and exits 2

### Contract: CYCLE_DRIVER_FALLS_BACK_TO_THE_TEMPLATE_ENGINE
- **Given:** a plant whose `docs/graph/grill-lint.py` carries no `plan_graph`
  or `pack`, beside the seed template at
  `docs/graph/templates/knowledge-graph/grill-lint.py`
- **When:** `cycle.py --unit U` runs
- **Then:** it reports the cycle read through the template and prints, after
  the header, `engine: docs/graph/templates/knowledge-graph/grill-lint.py,
  because docs/graph/grill-lint.py predates cycle.py (no plan_graph or pack);
  graft the plant to reconcile its engine`
- **And:** when no engine carries them, it exits 2 with
  `cycle: docs/graph/grill-lint.py: predates cycle.py (no plan_graph or pack), and so does every engine beside it; graft the plant`

## 5. Non-functional requirements

Stdlib Python on the seed's floor. The probes read the plant's files and run
nothing of the plant: `TEST_GLOBS` is read with `ast.literal_eval`, as the
worth check and the source index read it, and the engine is read as text. A
need adds nothing to the kernel or to any always-loaded prompt, and no step to
the seed's gate.

## 6. Data shapes

### Why a fifth set in the coverage record

The record's four sets did not fit. A collection is knowledge a scout
gathers; an agent or expert row is the roster; an inventory row is an item
the scouts found the project made of. A need is configuration a seed tool
reads from the plant, answered by the plant's own files, so the probe is its
answer and the record keeps only what a probe cannot see: the owner's
decision to go without. Existing declarations carry the facts themselves:
the model map, billing and token-usage lines in `docs/graph/models.md` (the
plant's configuration page, ADR-0022), the `trust:` field of crosscut nodes
(which `brief.py` already reads), `TEST_GLOBS` in `docs/graph/spec-lint.py`
(`grow.gate.spec-wired`), the gate table of `runbooks/verification.md`, and
the expertise node an inventory `language` row already owes.

### Why the audit is told it runs after a graft

Where a need blocks depends on the run: a fresh growth, a graft, daily work.
The audit takes it as an explicit option, `--after-graft`, with a fresh growth
the default, which graft Phase 5, `graft.gate.coverage` and
`tools/graft-run.py` pass. Inferring it from state was the other choice: the
record's `run` field, the stamp's history, or a record that predates the seed.
Each of those is a fact a later edit or an earlier run can leave behind, so a
wrong guess would block a graft or let a fresh growth through; the caller
always knows which run it is, so the caller says. Daily work needs no mode:
nothing a plant runs day to day runs the audit or reads a need
(NEED_BLOCKS_NO_DAILY_WORK).

### The needs (`NEEDS` in `tools/growth-audit.py`, the one home)

| Need | Owed by | Not configured while |
|---|---|---|
| `gate-output` | every plant | `runbooks/verification.md` is absent, still holds the `<gate>` row, or names no gate beyond the worth check |
| `cycle-driver` | every plant | `docs/graph/grill-lint.py` is absent or carries no `plan_graph` and `pack` |
| `model-map` | every plant | no map cell is filled; or a column of a stamped host that reads the map (`opencode`, `Prime Agent`) holds a placeholder |
| `cache-lifetime` | a plant with Claude Code | `Billing:`, `Lead cache lifetime:` or `Worker cache lifetime:` in `docs/graph/models.md` is absent or a placeholder |
| `token-ledger` | a plant with opencode, Prime Agent, Codex or GitHub Copilot | `Token usage:` in `docs/graph/models.md` is absent or a placeholder |
| `trust-paths` | every plant | no crosscut node under `docs/graph/nodes/` carries `trust: true` |
| `test-layout` | every plant | `TEST_GLOBS` is unset, or equal to the seed template's default |

A cell or line counts as filled when it holds no `<`; a `-` map cell is the
owner's explicit "inherit" and counts as filled.

### The `needs` row

`{"name", "what", "configured": bool, "detail", "status", "reason"}`. `--plan`
rewrites `what`, `configured` and `detail` from the probe and keeps `status`
and `reason`. `status: ABSENT` with a non-empty `reason` is the owner's
decision to go without.

### Output

`--plan`: `  PLANT NEED   <id> — not configured for this plant: <detail>. ...;
the coverage gate fails until then`, or with `--after-graft` `...; until then
the graft lists it under "Grafted but not yet grown" with its reason`.
Lint, fresh growth: `  UNGROWN      plant need <id>` and the indented
`not configured for this plant — <detail>. Supply <what> (grow.plant-needs), or
record the owner's decision to go without in this need's row of
.cypress/coverage.json: `status: ABSENT` with the owner's reason`.
Lint, after a graft: `  note: plant need <id> is not configured for this plant
— <detail>`, a missing testing idiom as `<slug>.testing-idiom`. A declined need
in either mode: `..., by the owner's decision: <reason>`; the passing summary line
`  coverage complete[ (<n> named blocker(s) carried)]; <n> plant need(s) not configured for this plant: <id>[ (declined)], ...`.
`--json`: `{"plant_needs": [{"name", "configured", "detail", "declined"}]}`
before the source-index item, listing the needs printed as notes (in a fresh
growth, the declined ones; an open one is among the verdicts).

## 7. Failure modes

### Failure: A_NEED_PROBE_READS_A_FORM_AS_A_FACT
- **Trigger:** a plant fills a line with text that holds no `<` but states
  nothing (a map cell `TODO`, a gate row that prints a whole log)
- **Response:** the need reads as configured; the probe checks that a fact
  was written, not that it is true
- **Recovery:** the Phase 6 validator and the reviewer read the runbook and
  the map (`grow.gate.executed`, `grow.gate.plant-needs`)

## 8. Examples

```
$ python3 <seed>/tools/growth-audit.py . <seed> --after-graft
  note: plant need gate-output is not configured for this plant — docs/graph/runbooks/verification.md still holds the template's placeholder gate row `<gate>`, so no gate of this plant is recorded as printing its failing ids ...
  note: plant need trust-paths is not configured for this plant, by the owner's decision: the owner decided on 2026-11-10 that this plant has no trust path
  audited 23 collection(s), 15 agent(s), 0 expert(s), 4 inventory item(s)
  coverage complete; 2 plant need(s) not configured for this plant: gate-output, trust-paths (declined)
```

## 9. Acceptance criteria

- [x] AC-1: a plant owes a row per need, named while open, closed when
  supplied, carried when declined, never blocking and never clean; maps to
  PLAN_OWES_A_ROW_PER_PLANT_NEED, UNCONFIGURED_NEED_IS_NAMED_AND_NEVER_BLOCKS,
  NEED_CLOSES_WHEN_THE_PLANT_SUPPLIES_IT, OWNER_DECLINED_NEED_IS_CARRIED_AS_NOT_CONFIGURED
- [x] AC-2: an untouched older model map and the hosts a plant runs are read
  from the plant, not from a template's bytes; maps to
  MODEL_MAP_NEED_READS_THE_CELLS_NOT_THE_BYTES, HOST_NEEDS_FOLLOW_THE_STAMPED_HOSTS
- [x] AC-3: a language's expertise node owns its testing idiom; maps to
  LANGUAGE_EXPERTISE_OWNS_ITS_TESTING_IDIOM
- [x] AC-5: an open need fails a fresh growth until supplied or declined, is
  a note after a graft (a missing testing idiom too), and blocks no daily
  work; maps to OPEN_NEED_BLOCKS_A_FRESH_GROWTH, PLAN_SAYS_WHERE_AN_OPEN_NEED_GOES,
  TESTING_IDIOM_IS_A_NOTE_AFTER_A_GRAFT, GRAFT_AUDITS_AS_AFTER_A_GRAFT,
  NEED_BLOCKS_NO_DAILY_WORK
- [x] AC-4: the cycle driver names a plan with no increments and drives an
  older plant through the template engine; maps to
  CYCLE_DRIVER_NAMES_A_PLAN_WITHOUT_INCREMENTS, CYCLE_DRIVER_FALLS_BACK_TO_THE_TEMPLATE_ENGINE

## 10. Test mapping

(Owned by `tester`.) The growth-audit cases run on a copy of the suite's green
all-ABSENT plant; the cycle cases on a copy of one fresh install. Every row was
`red` against the tools without the change first.

| Contract / Failure | Test case | Test file | Level | Status |
|---|---|---|---|---|
| PLAN_OWES_A_ROW_PER_PLANT_NEED | X665 scn_x665: five needs owed on a claude-code plant, cycle-driver met, token-ledger not owed; the record's six rows | tests/test-growth-audit.sh | integration (fixture) | green |
| UNCONFIGURED_NEED_IS_NAMED_AND_NEVER_BLOCKS | X666 scn_x665: after a graft, exit 0, one note per need, the summary lists them; the template runbook is named | tests/test-growth-audit.sh | integration (fixture) | green |
| NEED_CLOSES_WHEN_THE_PLANT_SUPPLIES_IT | X667 scn_x665: runbook, map, billing lines, a trust crosscut and TEST_GLOBS supplied; no line, plain summary | tests/test-growth-audit.sh | integration (fixture) | green |
| OWNER_DECLINED_NEED_IS_CARRIED_AS_NOT_CONFIGURED | X668 scn_x665: the declined row's reason printed, `(declined)` on the summary, kept by --plan | tests/test-growth-audit.sh | integration (fixture) | green |
| MODEL_MAP_NEED_READS_THE_CELLS_NOT_THE_BYTES | X669 scn_x665: the earlier template's text, untouched, is named unfilled; seen red first (the byte comparison printed nothing) | tests/test-growth-audit.sh | integration (fixture) | green |
| HOST_NEEDS_FOLLOW_THE_STAMPED_HOSTS | X670 scn_x665: opencode stamped, one opencode cell open, an older engine | tests/test-growth-audit.sh | integration (fixture) | green |
| LANGUAGE_EXPERTISE_OWNS_ITS_TESTING_IDIOM | X671 scn_x671: owed by --plan, HOLLOW without the key, closed with it; a runtime node is not held to it | tests/test-growth-audit.sh | integration (fixture) | green |
| OPEN_NEED_BLOCKS_A_FRESH_GROWTH | X720 scn_x720: five open needs fail the lint as UNGROWN with what satisfies each and the decline form; declined, exit 0; seen red first (exit 0, notes only) | tests/test-growth-audit.sh | integration (fixture) | green |
| PLAN_SAYS_WHERE_AN_OPEN_NEED_GOES | X721 scn_x720: the fresh plan's line says the gate fails, the after-graft plan's names the report section; seen red first (no such tail; the option unknown) | tests/test-growth-audit.sh | integration (fixture) | green |
| TESTING_IDIOM_IS_A_NOTE_AFTER_A_GRAFT | X722 scn_x671: after a graft the gap is a note, no HOLLOW, the exit code as with the key; seen red first (the option unknown) | tests/test-growth-audit.sh | integration (fixture) | green |
| GRAFT_AUDITS_AS_AFTER_A_GRAFT | X723 scn_x723: graft-run.py rehearses a green plant with five open needs; its coverage log notes each and its coverage gate is PASS, while the stage copy audited as a fresh growth fails UNGROWN; graft.md's commands carry the option (text check); seen red first with graft-run.py's coverage step built without `--after-graft` (no note in the coverage log) | tests/test-growth-audit.sh | integration (graft-run rehearsal) | green |
| NEED_BLOCKS_NO_DAILY_WORK | X724 scn_x724: an installed plant places no growth-audit.py, and only graph-lint.py names the record, reading no needs; characterization, green before the change | tests/test-growth-audit.sh | integration (fixture) | green |
| CYCLE_DRIVER_NAMES_A_PLAN_WITHOUT_INCREMENTS | X663 the template plan of a fresh install: one stderr line, exit 2; seen red first (an empty cycle, exit 0) | tests/test-cycle.sh | integration (temp install) | green |
| CYCLE_DRIVER_FALLS_BACK_TO_THE_TEMPLATE_ENGINE | X664 an older plant engine: the report through the template with its engine line; both engines older: the refusal; seen red first (refused at the first engine) | tests/test-cycle.sh | integration (temp install) | green |
| A_NEED_PROBE_READS_A_FORM_AS_A_FACT | none: a probe checks presence, a reviewer judges truth | none | none | none |

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Should the rows that predate the needs (collections, agents, experts, inventory) also turn to notes after a graft? | they still fail a graft's coverage gate, as they fail a fresh growth; the owner's decision of 2026-11-11 named the needs and the testing idiom | unchanged: they block in both runs, never day to day | owner | the owner's answer |
| How does a plant decline a language's testing idiom? | a fresh growth fails on it until the node owns the key, and no `needs` row carries it | the node owns the key; the row has no decline form yet | owner | the first plant whose language has no test idiom of its own |
| Should the testing idiom be owed by a framework row too? | a test framework is the idiom's other home | a `language` row owes it; its node may compose a framework's | architect | the first plant whose idiom lives in its framework |

## 12. Changelog

- 2026-11-10 — created by the implementer of the round's F3 and F4 work from
  the investigation of what the landed capabilities need from a plant. Nine
  contracts; each case seen failing first, then green.
- 2026-11-11 — the owner decided on 2026-11-11 that an open need blocks a
  fresh growth, is a note after a graft and never blocks daily work: five
  contracts added (OPEN_NEED_BLOCKS_A_FRESH_GROWTH to NEED_BLOCKS_NO_DAILY_WORK),
  three amended to run after a graft, the `--after-graft` option recorded in §6,
  and the open question on a graft's gate answered.
- 2026-11-11 — an independent tester read each contract and each cited case
  (X665 to X671 and X720 to X724 in `tests/test-growth-audit.sh`, X663 and
  X664 in `tests/test-cycle.sh`). Thirteen contracts are observable and their
  cases run the audit or the driver and watch exit codes, records and lines.
  X723 reads back source text for GRAFT_AUDITS_AS_AFTER_A_GRAFT; the tester
  sign is withheld until that contract has a run behind it (§11).
- 2026-11-11 — the open question on X723 is closed: GRAFT_AUDITS_AS_AFTER_A_GRAFT
  is now held by a run. X723 rehearses a graft with `tools/graft-run.py` over
  the green all-ABSENT plant with its five needs open (its one inventory row an
  incidental dependency, so the graft's own re-plan owes nothing new) and
  watches the outcome: each need is a note in the coverage log, the coverage
  gate passes, and the same stage copy audited as a fresh growth fails
  UNGROWN. The case was seen red with graft-run.py's coverage step built
  without `--after-graft`, then green on the real code; the source grep is
  gone, and the `protocols/graft.md` text check stays for the prose half. The
  contract's wording and its §10 row follow.
- 2026-11-11 — the independent tester re-reviewed X723 and signed as tester
  in §0. The rehearsal holds the contract by its outcome, with a control: the
  same copy audited as a fresh growth fails, so the passing gate comes from
  the option and not from a plant with nothing open. The `--plan` half of the
  coverage step changes only the wording of its prompt, which no gate reads,
  so the rehearsal does not watch it; that is accepted as the contract's soft
  part.
