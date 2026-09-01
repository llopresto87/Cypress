# grill — lean worker funnel, legal-in-architecture, ui-ux design surface

Plan-of-record for the 6.9.0 refactor. Objective (user): the grill funnel's
worker agents (tester, implementer, reviewer) consume too many tokens when
invoked as subagents — make them work smarter in smaller, well-defined steps;
wire `legal` into architectural work; add a definitive ui-ux-designer expert
with matching scout/growth facilities. Quality over size: no normative rule is
dropped; compression only where content is duplicated elsewhere (replace with a
pointer to the owning node). grill.md itself is touched minimally.

## §1 Artifact discovery (all read, paths cited)
- protocols/grill.md (6 950 B) — workflow, increment shape, alignment check.
- agents/02-implementer.md (7 995 B), 03-reviewer.md (8 421 B),
  04-tester.md (6 878 B) — the funnel workers; no per-spawn scope bound today.
- core/method/delegation.md — owns delegation.briefs (orchestrator-side brief
  discipline), the roster table.
- core/AGENTS.md kernel (7 046 B / 8 000 budget) — §1 roster list.
- agent-corpus/legal.md — optional legal role; corpus-only reasoning contract.
- agents/growth-scout.md, growth-orchestrator.md,
  templates/prompts/growth-scout-brief.md — growth facilities.
- agents/08-product.md — owns outcome/flows/acceptance/accessibility-floor
  (boundary for the new designer).
- tests/seed-lint.py — roster/manifest/kernel/README consistency; est_tokens
  within 2x of measured body; kernel budget; canonical-block byte-identity.
- integrations/claude-code/agent-lint.py + agents/_routes.golden.tsv — routing
  eval gate: top-1 >= 90%, novel rows LOW/NONE.
- Baseline: `bash tests/run.sh` fully green before this refactor.

## §6 Decisions
- D1 Per-spawn step contract, not gutted charters. Each funnel worker charter
  gains a "Scope of one spawn" section (tester: RED for ONE increment's named
  contracts; implementer: ONE RED→GREEN→REFACTOR cycle; reviewer: ONE diff for
  ONE increment) and briefs must carry the inputs (contract text, test paths,
  diff) so workers stop re-deriving context. Duplicated depth is replaced by a
  pointer to its owning node. Reversible; evidence: charters restate
  design/engineering-posture and holistic-editing content at length.
- D2 Orchestrator side of the same contract lives in method.delegation
  (`delegation.step-scope`): one well-defined step per spawn, inputs in the
  brief. One home per fact: each charter owns only its own scope section.
- D3 Legal stays an agent-corpus role (per-session economy stands) but becomes
  a NAMED CHECKPOINT of architectural work: architect charter + grill §11 step —
  when a boundary/contract/ADR implicates externally-authored rules (licenses,
  regulation, data protection, standards), route to `legal` (instantiate via
  the corpus withdraw contract if absent); a corpus gap is an open question,
  never a recalled rule. grill.md is otherwise untouched (user: quality over
  size; compress grill only if necessary — judged NOT necessary).
- D4 New base-roster agent `ui-ux-designer` (opus, authoring). Owns interface
  and interaction design: IA, screen flows, interaction states, design tokens /
  component system, usability heuristics, design specs under docs/graph/design/.
  Boundary: product keeps outcome/acceptance/accessibility floor;
  implementer keeps all production code. Triggers must not steal golden rows
  (esp. "define onboarding and the accessibility floor" → product).
- D5 Scout/growth facilities for the design surface: growth-scout-brief gains a
  design-surface evidence section (screens, components, tokens/styles, a11y
  state); growth-scout charter names that surface; growth-orchestrator may
  delegate design-surface node authoring to ui-ux-designer.
- D6 Behavior change ⇒ manifest 6.8.0 → 6.9.0 + CHANGELOG entry (append-only).

## §9 Increments (file ownership is disjoint)
- I1 (worker A, files: agents/02,03,04-*.md + core/method/delegation.md):
  step-contract rewrite of the three funnel charters + delegation.step-scope.
  Gate: seed-lint + agent-lint --lint/--eval green; all owns keys, triggers,
  handback sections preserved; est_tokens re-measured.
- I2 (worker B, files: agents/01-architect.md, protocols/grill.md,
  agent-corpus/legal.md): legal checkpoint in architecture + grill §11 hand-off
  + one corpus routing trigger. Gate: seed-lint + legal-lint green.
- I3 (worker C, files: agents/13-ui-ux-designer.md NEW, agents/growth-scout.md,
  agents/growth-orchestrator.md, templates/prompts/growth-scout-brief.md,
  scratch golden rows): designer charter + design-surface growth facilities.
  Gate: agent-lint --lint; canonical block in the brief template byte-identical.
- I4 (root): roster wiring (kernel §1, delegation table row, manifest agents,
  README, _routes.golden.tsv merge), version bump, CHANGELOG, full
  `bash tests/run.sh`.

## §10 Verification: `bash tests/run.sh` (9 suites + agent-lint lint/eval +
seed-lint + legal-lint) after I4; agent-lint --route spot-checks for the new
triggers; kernel stays under 8 000 B.

## §11 Risks
- New designer triggers steal top-1 from product/architect rows → eval gate
  catches; mitigation: avoid "accessibility floor / onboarding / acceptance"
  wording in triggers.
- Charter rewrite drops a normative rule → mitigation: workers must produce a
  rule-preservation table (old section → new home) in their summary; root
  reviews diff by diff.
- delegation.md edited by A and root → sequential (root integrates after A).

## §14 Recommended next step: spawn workers A, B, C in parallel.

## §15 Changelog
- 2026-09-01 root: plan created; baseline gates green.
- 2026-09-01 root: I1–I3 delivered by workers lean-funnel / legal-arch /
  design-surface (opus-4-8); I4 roster wiring done (kernel §1, delegation
  table, manifest 6.9.0, README 18-agent, graph index, 3 golden rows,
  tests/test_agent_lint.py ALL_AGENTS); CHANGELOG 6.9.0 entry appended.
  Full gate suite green (eval 100% 49/49). Review pass on opus-5 pending.
- 2026-09-01 root: opus-5 review returned APPROVE WITH MAJOR FIXES (0 critical,
  4 major, 7 minor; quality-over-size check passed). Fixed M1 (orchestrator
  allowlist += ui-ux-designer), M2 (product description defers interface
  design to ui-ux-designer + peer edge), M3 (templates/docs/design/ shipped:
  README, map entry, How-to-add row, librarian layout), M4 (architect legal
  spawn branch no longer promises allowlist wiring; fail-closed), minors m1
  (grill points at architect.legal-checkpoint for mechanics), m2 (reviewer DIP
  direction restored), m3/m4 (CHANGELOG accuracy). Suite green, exit 0.
  Committed and pushed to github remote per user instruction.
