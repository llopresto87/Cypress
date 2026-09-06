# grill — doctrine refinements (6.14.0)

Plan-of-record for seven refinements, each folded into an **existing** owner
rather than given a new subsystem. Objective: close gaps the graph does not
currently cover, without adding a second home for any fact it already owns.

## §1 Artifact discovery (all read, paths cited)

- `core/AGENTS.md` (7 180 B / 8 000 budget) — §3.x anchors, §4 boundaries.
- `protocols/verify.md` (236 L) — owns `rule.verify`, `verify.gate-states`,
  `verify.risk-depth`; gate table, risk-depth table, anti-patterns.
- `skills/holistic-editing/SKILL.md` (176 L) — owns `holistic-editing.method`,
  `.forbidden-moves`; prime directive, forbidden moves, **Scope rule**,
  append-only exception.
- `agents/02-implementer.md` (186 L) — §"Integrate, don't bolt on",
  §Preconditions, §"What you do not do".
- `agents/03-reviewer.md` — audits the forbidden moves.
- `core/method/engineering-posture.md` — owns `.sources-of-truth`,
  `.context-economy`, `.minimum-sufficient-work`, `.decision-economy`,
  `.integration-over-patching`, `.production-boundaries`.
- `core/method/design-posture.md` — owns `.right-sized-separation`,
  `.responsibilities`, `.cohesion-and-coupling`, `.dependency-direction`,
  `.state-and-policy`, `.anti-patterns`.
- `core/method/delegation.md` — owns `delegation.briefs` (+ roster, routing,
  model-classes, bounds, harness-registration, step-scope, turn, tracing,
  spec-authoring).
- `tests/seed-lint.py` — `KERNEL_BUDGET = 8_000`; `RULE_HOMES` (the eight
  `rule.*` keys); globally-unique `owns`; **est_tokens within 2x of measured
  body**; agnosticism/meta-fact checks.
- `tests/run.sh` — the gate runner (9 shell suites + graph-lint + agent-lint
  lint/eval + seed-lint + legal-lint; pytest gate SKIPs loudly when absent).
- `CLAUDE.md` — seed-maintainer conventions: behavior change ⇒ manifest bump +
  CHANGELOG entry; CHANGELOG and `docs/decisions/` are **append-only**;
  everything else integrate-don't-bolt-on.
- `docs/plans/grill-lean-funnel-design-legal.md` — precedent for a seed-side
  grill plan-of-record.

## §6 Decisions

**D1 — Fold into existing owners; create no new node.** Every rule here is an
extension of a fact the graph already reasons about. A new node would compete
for routing weight and dilute `owns:`. *Reversible.*

**D2 — Four new fact keys, not six.** `verify.absence-proof`,
`holistic-editing.class-sweep`, `engineering-posture.host-parity`,
`design-posture.baseline-preservation`. C3 (wired-in) and C6 (constraint
strength) are prose inside existing facts — C3 is charter behavior under
"Integrate, don't bolt on"; C6 is brief fidelity under `delegation.briefs`.
Minting a key for either would fragment a fact that already has a home.
*Reversible.*

**D3 — C6 does not go in the kernel.** 820 bytes of headroom remain, and §4 is
a list of hard prohibitions. A rule about *reading* constraint strength is not a
boundary; spending kernel rent on it is precisely the accumulation the budget
exists to prevent. *Irreversible-ish: moving it later means a kernel edit.*

**D4 — C2 is reconciled with the Scope rule in the text, not left implicit.**
See §11 R1. The Scope rule forbids chasing *different* problems; the class sweep
addresses *the same* problem in another location. Without an explicit
reconciliation the skill would carry two instructions that appear to conflict —
the exact defect `owns:` exists to prevent. *Reversible: drop C2.*

**D5 — C7 extracts, it does not reimplement.** `tests/seed-lint.py` keeps its
observable behavior and calls the shared implementation. Two copies of the
agnosticism check would violate one-home-per-fact in code. *Reversible.*

**D6 — Version 6.14.0 (minor).** Four new fact keys plus a new reusable tool is
additive capability, not a fix. *Reversible.*

**D7 — No ADR.** These strengthen existing decisions rather than making new
architectural ones. If C7's reuse surface is judged architectural, an ADR is
added then, not pre-emptively.

## §7 Options considered and discarded

- **A new `protocols/sweep.md` for C2.** Discarded: it would duplicate
  holistic-editing's unit-of-work reasoning and compete with it in routing.
- **A new `method/environment.md` for C4.** Discarded: host parity is a
  sources-of-truth question ("which machine is authoritative for this claim"),
  already an engineering-posture concern.
- **Putting C1 in `protocols/recover.md`.** Discarded: an unproven probe is not
  a failure to classify, it is a gate that did not mean what it said —
  `verify.gate-states` territory.
- **Kernel §4 bullet for C6.** Discarded per D3.

## §9 Implementation plan (increments)

| # | Increment | Files touched | Fact | Gate |
|---|---|---|---|---|
| I1 | Absence proof | `protocols/verify.md` | `verify.absence-proof` (new) | seed-lint (unique owns, est_tokens 2x), graph-lint |
| I2 | Class sweep | `skills/holistic-editing/SKILL.md` | `holistic-editing.class-sweep` (new) | seed-lint, graph-lint |
| I3 | Wire it in | `agents/02-implementer.md`, `agents/03-reviewer.md` | none (charter prose) | agent-lint --lint, --eval |
| I4 | Host parity | `core/method/engineering-posture.md` | `engineering-posture.host-parity` (new) | seed-lint, graph-lint |
| I5 | Baseline preservation | `core/method/design-posture.md` | `design-posture.baseline-preservation` (new) | seed-lint, graph-lint |
| I6 | Constraint strength | `core/method/delegation.md` | extends `delegation.briefs` | seed-lint |
| I7 | Agnosticism lint reuse | `tools/agnosticism-lint.py` (new), `tests/seed-lint.py`, `tests/test-agnosticism-lint.sh` (new), `tests/run.sh` | none | new suite + `test-seed-lint.sh` must still pass |
| I8 | Canonize | `CHANGELOG.md` (append), `manifest.json`, `DOCUMENTATION.md`, `documentation/README.md` | none | seed-lint version consistency |

Rollback path for I1–I6: each is a contained edit to one node; `git checkout` the
file. I7 is additive plus a behavior-preserving extraction; rollback restores
`seed-lint.py` and deletes the new files.

## §10 Verification plan

1. `python3 tests/seed-lint.py` — kernel budget untouched, `RULE_HOMES` intact,
   new `owns` keys globally unique, `est_tokens` within 2x of measured body.
2. `python3 templates/knowledge-graph/graph-lint.py` — no duplicate facts, no
   broken `requires:` edges.
3. `python3 templates/knowledge-graph/graph-lint.py --plan "<probe>"` × 3 —
   confirm new `load_when:` triggers resolve **and** that no existing route is
   displaced (`resolve()` is IDF-weighted top-3).
4. `python3 integrations/claude-code/agent-lint.py --lint --eval` +
   `agents/_routes.golden.tsv`.
5. `bash tests/run.sh` — full runner. Report executed vs SKIPped honestly;
   pytest is absent on this host so `test_agent_lint.py` will SKIP loudly.

## §11 Risks

**R1 — C2 tensions with holistic-editing's Scope rule.** *"Do not chase
unrelated code"* vs. sweeping siblings. Mitigation: D4's explicit
reconciliation, written into the section itself so the two are read together.
If the reconciliation is rejected, drop I2 rather than fudge it.

**R2 — Semantic overlap of new fact keys.** seed-lint catches a *collision*, not
an *overlap*. Mitigation: grep each concept across the graph before minting.

**R3 — `load_when:` additions degrade existing routing.** Mitigation: §10 step 3;
narrow triggers if a probe regresses.

**R4 — I7 breaks `test-seed-lint.sh`.** Mitigation: extract without changing
seed-lint's observable behavior; run that suite first.

**R5 — est_tokens drift.** Every touched node's `est_tokens` is re-measured, not
guessed; seed-lint enforces a 2x band.

## §13 Done criteria

- All seven rules present in their mapped owners, each reading as if it had
  always been there (no appended block, no duplicated fact).
- Four new fact keys, each owned in exactly one file.
- Kernel byte count unchanged.
- `bash tests/run.sh` green, with any SKIP named explicitly.
- Version bumped and CHANGELOG appended (never rewritten).
- Nothing project- or operator-identifying anywhere in the diff.

## §14 Recommended next step

Execute I1–I7, then I8, then run §10 in full.

## §15 Changelog

- 2026-09-06 — plan created. Seven refinements scoped, four fact keys decided,
  C6 kept out of the kernel (D3), C2 reconciliation made explicit (D4).
- 2026-09-06 — I1–I8 executed. Two fact keys renamed during implementation on
  a collision found by R2: `verify.absence-proof` → `verify.null-result` (the
  kernel §3.5 anchor already uses "absences" for a gate that did NOT run), and
  `design-posture.baseline-preservation` → `.restrictive-policy` (`verify.md`
  already uses "baseline" for the behavior-preservation oracle). R3 caught one
  real displacement: the trigger `"the scan came back clean…"` lowered the IDF
  weight of "clean" and pulled an extra node into an unrelated route; reworded
  to `"gate found nothing, zero results…"`, after which 0 of 157 baseline
  routes changed. I2 additionally amended the Scope rule, which had become
  incomplete rather than merely un-extended. A `--file` defect in the new
  `tools/agnosticism-lint.py` (bare `--file` fell through to the "." default
  and scanned the whole tree) was found in review, fixed, and pinned by a
  regression assertion verified RED against the defect and GREEN against the
  fix. ~~§10.5 predicted a pytest SKIP~~ — pytest is present on this host and
  `test_agent_lint.py` ran 44 passed / 1 skipped, that skip being a
  pre-existing environmental one (needs two golden-corpus copies to compare).
  Full `tests/run.sh` exit 0.
- 2026-09-06 — **I7 was deposited, not wired.** Review against harvest.md's own
  Phase 4 availability gate ("the import is WIRED into the downstream flow, not
  merely deposited") found the tool reachable only from `tests/run.sh` and the
  human documentation: no protocol node named it, and no plant received it, so
  an agent running harvest would read "grep the diff" and hand-roll one. Closed
  by naming it in `protocols/{harvest,graft,grow}.md` and `INSTALL_PROMPT.md`,
  delivering it via `install.sh place_graph_scaffold()` as config-free
  fast-forward machinery (the `agent-lint.py` class, not the add-if-missing
  `graph-lint.py` class), teaching `tools/graft-audit.py` to treat it as
  scaffold, and pinning delivery in `test-unified-graph-install.sh` and
  `test-full-install.sh` — both verified RED against the un-wired installer.
  Applicability is stated at every site: the lint applies to what a plant sends
  *up* (harvest candidates, declared-agnostic components), never to the plant's
  own knowledge, which SHOULD name the project. An unconditional gate here
  would be the failure `design-posture.restrictive-policy` (C5, this same
  release) exists to prevent.

