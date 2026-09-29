# grill.md: Plan of Record: proportionate checks (defect D2)

## 0. Metadata
- Project: CYPRESS seed
- Goal: one principle, "proportionate checks", with one home, so the seed stops driving test scope creep and stops pushing checks into delivered systems' automated runs and running code (owner, D2)
- Date: 2026-09-29
- Owner: the steward; the orchestrating session plans, briefs and commits
- Tier: T3. Protocol: `protocol.grill`. The owner approved the session plan
- Current phase: architect pass complete (this file); the implementer batch has not started
- Source: the plant's session plan `docs/graph/plans/sessions/2026-09-29-proportionate-checks.plan.md` (problem, the five causes, constraints; not restated here) and `docs/defect-notes.md` D2 (owner's words)
- Related specs: none. No seed spec owns these nodes' wording (see §6, D4)
- Version: not recorded (the release name is the session's call)

## 1. The principle, final wording

Home: `skill.test-first` (`skills/test-first/SKILL.md`), slug `test-first.proportionate-checks`, replacing `test-first.lean-suite`. The block below is E3's new text, verbatim:

````text
## Proportionate checks (`test-first.proportionate-checks`)

The one home for when a check exists and what it may cost. A check is a
test, a gate, or a check inside delivered code (validation, a guard, a
fail-closed path). Other nodes link here; they do not restate it.

- **A check exists only for a named, real blast radius.** Name what
  breaks, and for whom, if the check is absent. No name, no check. Spec
  size does not set test count: one test may cover several failure
  modes, and a failure mode with no real blast radius gets none.
- **A test is cheaper than its subject.** It asserts one behavior and
  never re-implements the code under test. A test that would need more
  code than its subject means the level or the design is wrong: hand
  it back unwritten, with that finding.
- **Full rigor is for high blast radius only.** Mutation proof,
  prefix/suffix mutants, and planted violations re-run after a refactor
  belong to the classes `delegation.mutation-at-end` makes mandatory,
  and run once per batch under that rule. Elsewhere a RED seen failing
  for the right reason is the proof, plus any sample that rule records.
- **The owner adds checks to runs; the seed adds none.** A new check
  joins the project's automated runs, or the running product, only by
  a recorded owner decision. An escaped bug earns a regression test; a
  new gate is `protocol.verify-new-gates`'s call.
- **Shrink on purpose.** A suite only grows unless someone cuts it.
  Where several tests pay for one expensive action, run it once and
  assert each outcome under its own name. Every deleted test names its
  survivor, the test that still fails when it would have; with no
  survivor the deletion is a recorded coverage loss. Consolidation is
  its own planned increment (`protocol.grill`). The tool corpus
  catalogs a lint for suite smells,
  `tool-corpus/testing/test-hygiene-lint.md`.
````

Why this home (D1 in §6): the test is the check the seed writes most; the skill is a small tier-2 leaf that every test-shaping and suite-shrinking task already loads; it already owned the suite-size rule this replaces. `protocol.verify` (469 lines) and the posture nodes are costlier to load for a one-line answer, and each of them now links here.

## 2. Node edits (exact strings)

Apply each as one exact-string replacement; every "Replace" string below occurs exactly once in its file (checked against the files on 2026-09-29). Nodes other than the home carry a link, not a restatement.

### `skills/test-first/SKILL.md`

**E1** (owns slug renamed). Replace:

````text
  - test-first.lean-suite
````

with:

````text
  - test-first.proportionate-checks
````

**E2** (route to the principle). Replace:

````text
  - "consolidate or shrink a test suite, duplicate or expensive tests"
````

with:

````text
  - "consolidate or shrink a test suite, duplicate or expensive tests"
  - "does this test, gate or runtime check earn its place, how much rigor"
````

**E3** (lean-suite section replaced by the principle). Replace the whole section, from its heading to the line before `## Reference files`:

````text
## Keeping the suite lean (`test-first.lean-suite`)

Every increment adds its own tests, so a suite only grows unless
someone shrinks it on purpose. Duplicates and repeated expensive setup
pile up unseen until the whole suite is measured.

- **Consolidate by action, not by safe fold.** Where several tests pay
  for the same expensive action (a repository copy, a fresh
  environment, a full gate run), run the action once and assert each
  outcome under its own name. Per-stage happy-path tests that one
  end-to-end chain run already covers go; so do tests written for one
  real consumer (above) and tests that assert nothing a sibling does
  not. Merging only the folds that are obviously safe lowers the count
  and leaves the cost where it was.
- **A size target is an aspiration, never a quota.** A number chosen
  up front is a direction, not something to delete toward.
- **Every deleted test names its survivor**: the test that still fails
  when the deleted test would have (the one that still kills its
  mutants). With no survivor, the deletion is a coverage loss and is
  recorded as one. A reduction pass that ends with more tests than it
  started with owes an explanation for each addition.
- **Consolidation is planned work.** Schedule it once the spec's
  behavior has landed, as its own increment in the plan-of-record
  (`protocol.grill` owns increment order). Run mid-spec, beside the
  critical path, it competes with the work it should follow.
- **Review for the smells that inflate a suite**: byte-identical test
  bodies, several tests calling the same expensive helper with the same
  arguments, and expensive per-test setup. The seed's tool corpus
  catalogs a lint that flags them,
  `tool-corpus/testing/test-hygiene-lint.md`.
````

with the §1 block, verbatim (it ends with one blank line before `## Reference files`).

### `protocols/test-first.md`

**E4** (mutation proof risk-tiered and batched). Replace:

````text
**Inherited suites — prove RED by mutation.** A suite you inherited
that was authored without test-first, and that is green the moment you
arrive, is untrusted: you have never watched it fail, so you do not
yet know it asserts anything. Before you rely on it, do the
adoption-time analog of RED — deliberately reintroduce in the
production code the historical defect a test claims to guard against,
confirm the suite fails for *that specific reason*, then revert. Only
a green you have seen turn red and back is a trusted green.
````

with:

````text
**Inherited suites — prove RED by mutation.** A suite you inherited
green, authored without test-first, is untrusted: you have never
watched it fail. Before you rely on a test over high blast-radius code,
reintroduce in the production code the historical defect it claims to
guard against, confirm it fails for *that specific reason*, then
revert. Which code earns this, and when it runs (once per batch), is
`test-first.proportionate-checks`.
````

### `agents/04-tester.md`

**E5** (tests by risk, not one per §7 item). Replace:

````text
3. For each failure mode in spec §7, write a test that triggers it
   and asserts the documented behavior.
````

with:

````text
3. Test a spec §7 failure mode only where its blast radius is named
   and real (`test-first.proportionate-checks`); a test that needs more
   code than its subject goes back in the handback, unwritten.
````

**E6** (follows item 3). Replace:

````text
   for each contract and each failure mode, status `red`.
````

with:

````text
   for each contract and each failure mode tested, status `red`.
````

**E7** (drops the mandate to add the suite to automated runs). Replace:

````text
Treat the eval suite like any other test suite: it runs in CI, it
gates the increment, its results go in
`docs/graph/runbooks/verification.md`.
````

with:

````text
Treat the eval suite like any other test suite: it gates the
increment, and its results go in `docs/graph/runbooks/verification.md`.
````

**E8** (escaped bug earns a test, not automatically a gate). Replace:

````text
When a kind of bug slips past the existing gates, add a new gate
that would have caught it (and a test that reproduces the bug).
This is the only way the gate set converges on real coverage.
````

with:

````text
When a bug slips past the existing gates, write the test that
reproduces it; whether a new gate follows is `protocol.verify-new-gates`.
````

### `protocols/verify.md`

**E9** (link to the home). Replace:

````text
Select the gates that apply to the change. Use the lowest level that
catches the kind of bug you care about; don't run every gate on every
change.
````

with:

````text
Select the gates that apply to the change, at the lowest level that
catches the bug. Whether a check exists at all is
`test-first.proportionate-checks`.
````

**E10** (absent-list sized by blast radius, not the standard gate list). Replace:

````text
   not an excuse to leave the runbook empty: record each standard gate
   explicitly as `absent (YYYY-MM-DD) — <reason>`. A blank verification
````

with:

````text
   not an excuse to leave the runbook empty: record each gate its blast
   radius calls for as `absent (YYYY-MM-DD) — <reason>`. A blank verification
````

**E11** (gate by owner decision; repeat planted violation only at high blast radius). Replace:

````text
   evidence, and do not wire such a gate into CI. Land the real check
   first (a test that asserts, a rule that fires); *then* add the gate,
   in a later increment — never both in the same one. A gate is trusted
   only once a **planted violation** has turned it red, naming the
   offender, and the plant's removal has turned it green again; that
   demonstration is part of the gate's record, and is repeated after any
   refactor around the assertion — a surviving tautology is worse than a
   deleted check.
````

with:

````text
   evidence, and do not make it a gate. Land the real check first (a
   test that asserts, a rule that fires); the gate follows in a later
   increment, by owner decision (`test-first.proportionate-checks`). A
   gate is trusted only once a **planted violation** has turned it red,
   naming the offender, and its removal has turned it green again; that
   demonstration is part of the gate's record. Over high blast-radius
   code it is repeated, once per batch, after a refactor around the
   assertion — a surviving tautology is worse than a deleted check.
````

**E12** (anti-pattern that made every gate an automated-run gate; deleted). Replace:

````text
- "Tests pass locally, didn't run them in CI." If the gate isn't in
  CI, it isn't a gate; it's a hope.
````

with:

nothing (delete both lines).

### `protocols/verify-new-gates.md`

**E13** (gate on recurrence or high blast radius; no automatic addition; duties cut to two). Replace:

````text
If verification reveals a kind of bug that no existing gate would have
caught, add a gate. New gates:
- Pick the lowest level that catches the bug.
- Get a test case that reproduces the bug (RED).
- Get added to the verification runbook in the same increment.
- Get added to CI in the next reliability-owned increment.

A gate is a tool, and a tool that can fail halfway is a second thing to
verify. Any gate or verification script you author is **all-or-nothing**:
it validates everything it will touch before it writes anything, so a
failure never leaves a half-applied state; it runs under strict error
and unset-variable handling and resolves its own root from its location,
never from the working directory; and it keeps **environment failures
distinct from repository failures** in both remedy text and exit status
— a missing interpreter, an absent fixture, or a tool that could not
start never degrades into a skip or an empty success, or a broken
environment reads as a clean tree. Fixtures raise on an environment
fault and reserve the empty result for a genuine empty success. Fail
closed by default; a soft mode for local troubleshooting is an explicit,
documented switch. Whether a check deserves to become a cataloged tool
at all is `toolcraft`'s doctrine.
````

with:

````text
If verification reveals a kind of bug that no existing gate would have
caught, write the test that reproduces it (RED). A new gate is owed only
when that kind of bug recurs or its blast radius is high
(`test-first.proportionate-checks`). A new gate takes the lowest level
that catches the bug, is recorded in the verification runbook in the
same increment, and joins the project's automated runs only by owner
decision.

A gate or verification script that writes never leaves a half-applied
state, and it keeps **environment failures distinct from repository
failures**: a missing interpreter, an absent fixture, or a tool that
could not start never reads as a skip, an empty success, or a clean
tree. Any further hardening is sized by the same principle. Whether a
check deserves to become a cataloged tool at all is `toolcraft`'s
doctrine.
````

### `core/method/release-posture.md`

**E14** (mandated set becomes conditional). Replace:

````text
may spend. Four supply-chain gates run in CI — advisories failing on
high severity, committed-secret scanning, static analysis for injection
patterns, image scanning under the pinned-tag policy — each with the
positive control `protocol.verify` requires of a zero.
````

with:

````text
may spend. Supply-chain gates (high-severity advisories, committed
secrets, injection patterns, image scanning under the pinned-tag policy)
are adopted one by one where the blast radius is named
(`test-first.proportionate-checks`), each with the positive control
`protocol.verify` requires of a zero.
````

### `core/method/engineering-posture.md`

**E15** (runtime all-or-nothing duties scoped by blast radius). Replace:

````text
When a boundary persists durable state, write it so a crash leaves
either the complete old value or the complete new one, never a partial
write; and when persistent state is read back corrupt, quarantine the
bad artifact for inspection, recover to a safe empty or partial state,
and surface the fault — never fail silently, and never silently
discard.
````

with:

````text
When a boundary persists state whose loss or corruption has a named
blast radius (`test-first.proportionate-checks`), write it so a crash
leaves the complete old value or the complete new one; when such state
reads back corrupt, quarantine it, recover to a safe state, and surface
the fault. Never fail silently, and never silently discard.
````

### `skills/toolcraft/SKILL.md`

**E16** (tool tests and checks follow the cost test). Replace:

````text
- is **authorized by a test** (§3.4) — at least one test pins what it
  does, so a future session can trust and change it safely;
````

with:

````text
- is **authorized by a test** (§3.4) — at least one test, sized by
  `test-first.proportionate-checks`, pins what it does;
````

### `agents/02-implementer.md`

**E17** (runtime checks follow the cost test). Replace:

````text
- **Encode assumptions** as validation, type signatures, and tests.
````

with:

````text
- **Encode assumptions** in types and tests; a runtime check must earn
  its place (`test-first.proportionate-checks`).
````

### `the runbook template `verification.md` (templates, docs tree)`

**E18** (starts minimal). Replace:

````text
| Gate | Command | Expected outcome | Trusted since |
|---|---|---|---|
| formatter   | `<cmd>` | exit 0, no diff | `<date>` |
| linter      | `<cmd>` | exit 0, no warnings above threshold | `<date>` |
| type check  | `<cmd>` | exit 0 | `<date>` |
| unit tests  | `<cmd>` | exit 0, N cases pass | `<date>` |
| integration | `<cmd>` | exit 0 | `<date>` |
| build       | `<cmd>` | artifact produced | `<date>` |
| smoke test  | `<cmd>` | deployed system responds 200 to `/health` | `<date>` |
| eval suite  | `<cmd>` | rubric score >= gate threshold | `<date>` |
````

with:

````text
List only the gates the project's blast radius calls for
(`test-first.proportionate-checks`); a row is added by owner decision.

| Gate | Command | Expected outcome | Trusted since |
|---|---|---|---|
| `<gate>` | `<cmd>` | `<exit status and what it asserts>` | `<date>` |
````

## 3. Mechanical fallout (not doctrine; keeps mirrors and section names true)

**E19** `documentation/skills-and-templates-reference.md` (mirror paragraph follows the node; apply before E20). Replace:

````text
**Keeping the suite lean (`test-first.lean-suite`).** A suite only grows
unless someone shrinks it on purpose. Consolidate by the expensive action
several tests share, not by a safe-looking fold; treat a size target as a
direction, never a quota; every deleted test names the survivor that still
kills its mutants; schedule consolidation as its own increment, never mid-spec;
and review for the smells `tool-corpus/testing/test-hygiene-lint.md` catalogs
— byte-identical bodies, repeated expensive helpers, expensive per-test setup.
````

with:

````text
**Proportionate checks (`test-first.proportionate-checks`).** A check (test,
gate, or check in delivered code) exists only for a named, real blast radius; a
test is cheaper than its subject and never re-implements it; full rigor is for
high blast radius, once per batch; a new check joins the automated runs or the
running product only by owner decision. Every deleted test names its survivor,
and consolidation is its own planned increment.
````

**E20** `documentation/skills-and-templates-reference.md` (slug rename). After E19, replace the two remaining `test-first.lean-suite` with `test-first.proportionate-checks`: the summary-table row and the per-skill `owns` line. `tests/seed-lint.py` holds this file to the node's frontmatter.

**E21** `protocols/grill.md` (section name follows the rename). Replace:

````text
then merge or delete under the lean-suite rules in
````

with:

````text
then merge or delete under the proportionate-checks rules in
````

**E22** `tool-corpus/testing/test-hygiene-lint.md` (section name). Replace:

````text
default (owned by `skills/test-first/SKILL.md` "Keeping the suite lean",
````

with:

````text
default (owned by `skills/test-first/SKILL.md` "Proportionate checks",
````

**E23** `tool-corpus/testing/test-hygiene-lint.md` (section name). Replace:

````text
  "Keeping the suite lean" owns the review-level default this lint checks
````

with:

````text
  "Proportionate checks" owns the review-level default this lint checks
````

`est_tokens`: leave every frontmatter value as it is unless a lint names one; if a lint does, change the node and its row in `documentation/skills-and-templates-reference.md` or `documentation/protocols-reference.md` together (seed-lint holds them equal).

## 4. Line delta

| File | Lines before | Lines after | Delta | Why, if it grows |
|---|---|---|---|---|
| `skills/test-first/SKILL.md` | 126 | 128 | +2 | the home: the principle replaces `lean-suite` (31 lines out, 32 in) and gains one routing phrase so a session asking "does this check earn its place" lands here |
| `protocols/test-first.md` | 329 | 328 | -1 |  |
| `agents/04-tester.md` | 201 | 200 | -1 |  |
| `protocols/verify.md` | 469 | 467 | -2 |  |
| `protocols/verify-new-gates.md` | 83 | 77 | -6 |  |
| `core/method/release-posture.md` | 236 | 237 | +1 | the fixed set becomes a conditional one; the condition and its link cost one line |
| `core/method/engineering-posture.md` | 211 | 210 | -1 |  |
| `skills/toolcraft/SKILL.md` | 152 | 152 | +0 |  |
| `agents/02-implementer.md` | 221 | 222 | +1 | the one-line link wraps to two lines; the only rule in the charter that invites runtime checks |
| `the runbook template `verification.md` (templates, docs tree)` | 73 | 69 | -4 |  |
| `documentation/skills-and-templates-reference.md` | 1807 | 1806 | -1 |  |
| `protocols/grill.md` | 361 | 361 | +0 |  |
| `tool-corpus/testing/test-hygiene-lint.md` | 200 | 200 | +0 |  |
| **Total** | | | **-12** | net-negative |

Two nodes grow by one line and the home by two; the reasons are in the table. The batch fails if the total is not negative.

## 5. Term check

New text (§1, E1 to E23): zero runner-, host- or delivery-specific words. Checked with a scan for CI, CD, pipeline, workflow, vendor names, YAML, cron, runner, host, container, hook. The one hit, "action" in "one expensive action", is plain English.

Existing terms seen in the edited nodes, left as they are because no edit touches the sentence (findings, not edits; line numbers are before the batch):
- `protocols/test-first.md` :326-329, anti-pattern "Assuming dev-machine green means CI green" (CI three times).
- `agents/04-tester.md` :74, heading "Spec → test pipeline".
- `protocols/verify.md` :274-275, "CI is a caller of that entry point, never a second home for the checks."
- `core/method/release-posture.md` :147, "(a local suite, a pipeline, a deploy-time scan)".

Removed by the edits because they sat in touched sentences: "CI" in `agents/04-tester.md` :129, `protocols/verify.md` :359 and :428-429, `protocols/verify-new-gates.md` :61, `core/method/release-posture.md` :177.

## 6. Decisions Made

| Decision | Rationale | Evidence | Reversibility | ADR | Date |
|---|---|---|---|---|---|
| D1: the principle's home is `skill.test-first` | see §1 | session plan §3 | reversible | none | 2026-09-29 |
| D2: the batching rule is linked, not restated; the mandatory classes stay with `delegation.mutation-at-end` | one home per fact | `core/method/delegation-cycle-economy.md` "Mutation at the end" | reversible | none | 2026-09-29 |
| D3: spec §4 contracts still get one test each (a test may cite several slugs); only §7 failure modes become risk-selected | `spec-lint.py` holds live contracts to a named test; changing that is a separate decision | `protocols/verify.md` gate table, Spec-coverage lint | reversible | none | 2026-09-29 |
| D4: slug renamed, not kept beside a new one | two slugs for one rule would be two homes | `skills/test-first/SKILL.md` frontmatter | reversible | none | 2026-09-29 |
| D5: toolcraft's "Fail-closed doctrine" heading stays | it names a completion rule (catalog or record), not a runtime duty; five other files cite it by that name | `protocols/canonize.md`, `agents/09-docs-librarian.md` | not applicable | none | 2026-09-29 |

## 9. Implementation Plan

### Increment 1: all edits, one batch
- Item: D2 (class P)
- Spec contracts: none. Why: node wording only; no seed spec owns it; the owner approved the session plan
- Files touched: the ten nodes in §2, plus `documentation/skills-and-templates-reference.md`, `protocols/grill.md`, `tool-corpus/testing/test-hygiene-lint.md` (§3)
- Tests to write (RED): none. Doctrine text; no behavior of seed code changes
- Behavior added: none
- Gate: after all edits, once: `bash tests/run.sh` from the seed root (it runs the suite and the lints: seed-lint, agent-lint, graph-lint tests, prose-lint, ratchet-lint, gate-registry). Record the §4 delta measured with `wc -l`
- Expected fallout: a test that goes red because it pins old node wording is listed in the handback by name as an owner deletion candidate. It is never "fixed" by restoring the wording. Any other red is a real finding and stops the batch
- Rollback path: revert the one commit
- Effort: medium
- Phase: GREEN (implementer)
- Depends on: none

### Increment 2: close-out
- Item: D2 (class P)
- Spec contracts: none
- Files touched: `CHANGELOG.md` (humanized), `docs/defect-notes.md` D2 status line, the session record
- Tests to write (RED): none
- Gate: the CHANGELOG entry passes `python3 tools/prose-lint.py --file CHANGELOG.md` if run.sh does not already cover it
- Rollback path: revert
- Effort: low
- Phase: canonize (docs-librarian)
- Depends on: increment 1

## 12. Open Questions (owner)

1. `delegation.mutation-at-end` samples mutation outside the mandatory classes by default. Should the default become "none unless the owner widens it"? §1 defers to that rule either way.
2. `protocols/verify.md` :57-60 says a rule is a control only when wired into a gate. Read with the verify rule, it still pulls each binding rule toward a gate. Scope it by blast radius in a later pass?
3. The four existing term hits in §5: rewrite them in a later pass?

## 13. Done Criteria

- `test-first.proportionate-checks` exists once, in `skills/test-first/SKILL.md`; every node in §2 links to it.
- The §4 total is negative, measured.
- `tests/run.sh` reds, if any, are only wording-pin tests, listed by name for the owner.

## 15. Changelog

- 2026-09-29: plan written by the architect (spawn `session.1.architect.1`).
- 2026-09-29: increment 1 applied by the implementer (spawn `session.2.implementer.1`): E1-E23 + Q1-Q3 (owner rulings), delta -10, suite 48/50 (test-knowledge-paths: this file's path, fixed by the session; GR-h: fixture assumes an untagged checkout, carried to the test review).
