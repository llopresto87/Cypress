---
status: back-written
status_date: 2026-11-10
owner: architect
status_evidence: tests/test-growth-audit.sh (X665 to X671) and tests/test-cycle.sh (X663, X664), wired into tests/run.sh through their existing steps; every case was seen failing first against the tools without the change (no PLANT NEED line, no testing-idiom finding, the old model-map byte comparison, an empty cycle printed with exit 0, a refusal at the first older engine), then green
---

# SPEC-0011: grown, not carried

## 0. Metadata

- **Identifier:** SPEC-0011-grown-not-carried
- **Status:** see frontmatter (single home)
- **Owner:** architect
- **Date:** 2026-11-10
- **Last reviewed:** 2026-11-10
- **Related grill section:** docs/plans/grill-8.5.0-tester-surfaces.md, the
  requirements that carry the earlier rounds through to plants (F3, F4)
- **Related ADRs:** adr-0022-the-plant-model-map (an unfilled map means
  inherit, disclosed and passed); adr-0034-a-test-is-owed-only-where-it-can-catch-something
  (the trust-path reading and the testing idiom a tester writes against);
  adr-0003-enforcement-layering-honesty (a need is detective: it names, it
  never blocks)
- **Related specs:** SPEC-0005-cycle-economy (the cycle driver, the token
  ledger, the model classes); SPEC-0006-session-metrics (the `Tokens` line
  that may read `not recorded`); SPEC-0008-who-writes-the-test (the
  trust-path reading); SPEC-0009-worth-check (the same `TEST_GLOBS`)
- **Related wiki pages:** none (stdlib Python only)
- **Design latitude:** balanced. A need never fails the growth gate, because
  every capability it serves has a safe default; it is never reported clean
- **Supersedes:** none
- **Superseded by:** none
- **Sign-offs:** product [ ] · architect [ ] · tester [ ]
  Back-written on 2026-11-10 by the implementer of the round's F3 and F4
  work, after each case was seen red and then green; no promotion was signed.
  The round's architect and tester review it before it is promoted.

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
it while it is not configured, and it closes when the plant supplies it.

## 2. Scope

In scope: the `needs` rows of `.cypress/coverage.json`, the probes that answer
them, their lines in `--plan` and the lint, the testing-idiom finding on a
language's expertise node, and the cycle driver's two unconfigured states.

Out of scope: any change to what a capability does when its fact is absent
(each keeps its safe default); the opencode lead's launch list for a plant's
own expert, and an unknown tool name in a plant's agent, which wait on the
owner (`docs/plans/owner-decisions-8.5.0-tester-surfaces.md`).

## 3. User-facing behavior

`growth-audit.py <plant> <seed> --plan` prints, beside its other prompts,
`PLANT NEED   <id> — not configured for this plant: <what is missing>. Supply
<what> (grow.plant-needs), or record the owner's decision to go without in
this row` for each open need, and writes one `needs` row per need the plant
owes. The lint prints `note: plant need <id> is not configured for this plant
— <what is missing>` after its verdicts, and a passing run ends
`coverage complete; <n> plant need(s) not configured for this plant: <ids>`
instead of a bare `coverage complete`. The exit code is the verdicts' alone.

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
- **When:** the lint runs
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
- **When:** the lint runs, and `--plan` runs again
- **Then:** the lint prints `note: plant need <id> is not configured for this
  plant, by the owner's decision: <reason>`, lists it as `<id> (declined)` on
  its summary line, and exits 0; `--plan` keeps the status and the reason

### Contract: MODEL_MAP_NEED_READS_THE_CELLS_NOT_THE_BYTES
- **Given:** a `docs/graph/models.md` copied from an earlier seed's template
  and never edited (its text differs from today's template; every map cell
  still holds its placeholder)
- **When:** the lint runs
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

`--plan`: `  PLANT NEED   <id> — not configured for this plant: <detail>. ...`.
Lint: `  note: plant need <id> is not configured for this plant — <detail>`, or
`..., by the owner's decision: <reason>`; the passing summary line
`  coverage complete[ (<n> named blocker(s) carried)]; <n> plant need(s) not configured for this plant: <id>[ (declined)], ...`.
`--json`: `{"plant_needs": [{"name", "configured", "detail", "declined"}]}`
before the source-index item.

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
$ python3 <seed>/tools/growth-audit.py . <seed>
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
| UNCONFIGURED_NEED_IS_NAMED_AND_NEVER_BLOCKS | X666 scn_x665: exit 0, one note per need, the summary lists them; the template runbook is named | tests/test-growth-audit.sh | integration (fixture) | green |
| NEED_CLOSES_WHEN_THE_PLANT_SUPPLIES_IT | X667 scn_x665: runbook, map, billing lines, a trust crosscut and TEST_GLOBS supplied; no line, plain summary | tests/test-growth-audit.sh | integration (fixture) | green |
| OWNER_DECLINED_NEED_IS_CARRIED_AS_NOT_CONFIGURED | X668 scn_x665: the declined row's reason printed, `(declined)` on the summary, kept by --plan | tests/test-growth-audit.sh | integration (fixture) | green |
| MODEL_MAP_NEED_READS_THE_CELLS_NOT_THE_BYTES | X669 scn_x665: the earlier template's text, untouched, is named unfilled; seen red first (the byte comparison printed nothing) | tests/test-growth-audit.sh | integration (fixture) | green |
| HOST_NEEDS_FOLLOW_THE_STAMPED_HOSTS | X670 scn_x665: opencode stamped, one opencode cell open, an older engine | tests/test-growth-audit.sh | integration (fixture) | green |
| LANGUAGE_EXPERTISE_OWNS_ITS_TESTING_IDIOM | X671 scn_x671: owed by --plan, HOLLOW without the key, closed with it; a runtime node is not held to it | tests/test-growth-audit.sh | integration (fixture) | green |
| CYCLE_DRIVER_NAMES_A_PLAN_WITHOUT_INCREMENTS | X663 the template plan of a fresh install: one stderr line, exit 2; seen red first (an empty cycle, exit 0) | tests/test-cycle.sh | integration (temp install) | green |
| CYCLE_DRIVER_FALLS_BACK_TO_THE_TEMPLATE_ENGINE | X664 an older plant engine: the report through the template with its engine line; both engines older: the refusal; seen red first (refused at the first engine) | tests/test-cycle.sh | integration (temp install) | green |
| A_NEED_PROBE_READS_A_FORM_AS_A_FACT | none: a probe checks presence, a reviewer judges truth | none | none | none |

## 11. Open questions

| Question | Why it matters | Current assumption | Owner | Resolves by |
|---|---|---|---|---|
| Should an open need block a graft's coverage gate? | a need never blocks, so a graft can close with every need open | named in the delivery and the changelog (`grow.gate.plant-needs`), as an UNKNOWN row is | owner | the first graft whose delivery drops an open need |
| Should the testing idiom be owed by a framework row too? | a test framework is the idiom's other home | a `language` row owes it; its node may compose a framework's | architect | the first plant whose idiom lives in its framework |

## 12. Changelog

- 2026-11-10 — created by the implementer of the round's F3 and F4 work from
  the investigation of what the landed capabilities need from a plant. Nine
  contracts; each case seen failing first, then green.
