# ADR-0001: Mechanical agent-router (`agent-lint.py --route`) fed by `routing_triggers` frontmatter

## Status

`accepted` — implemented and verified 2026-07-13 (plan §9, P0).

> This ADR is the standalone promotion of **ADR-A**, decided inline at
> `../plans/agent-routing-and-delegation.md` §3. The plan's §3 body remains the
> faithful source; this file restates it and links back. Do not re-decide here.

## Date

2026-07-13

## Context

The seed had exactly one deterministic routing mechanism — the **knowledge**
router (`docs/graph/graph-lint.py --plan` + `.claude/route-hook.py`) — and it
routes knowledge *nodes*, never *agents* (plan §1, RC1). Specialist selection
was therefore 100% orchestrator model-judgment reading prose `description:`
frontmatter, with no executable floor, no confidence signal, and nothing
citable in a delegation brief. The operator observed frequent mis-routing to
the wrong specialist (problem A). The cheap decision (which docs to read) was
mechanized; the expensive one (which expert does the work) was left to
unassisted judgment.

## Decision

Ship `agent-lint.py` mirroring `graph-lint.py`'s parser and IDF-weighted
`resolve()`; add a required non-empty `routing_triggers:` list to every agent's
frontmatter as the high-signal routing index (the agent analog of a node's
`load_when:`). `agent-lint.py --route "<task>"` returns a ranked specialist list
with scores and a confidence band (HIGH / MEDIUM / LOW / NONE), to be **cited in
every delegation brief**. It is a *heuristic floor*, not an oracle — the
orchestrator still reasons over it, mirroring the honesty of
`context-router/SKILL.md` ("`--plan` is a keyword heuristic").

## Consequences

- Every agent frontmatter gains `routing_triggers` (P0 added this to all 13);
  `agent-lint.py --lint` enforces presence/non-emptiness and warns on
  non-distinctive triggers (the IDF analog of graph-lint's fact-distinctiveness).
- A new gate exists: `agent-lint.py --eval` runs the golden routing set
  (`_routes.golden.tsv`) and asserts top-1 accuracy + novel-stack LOW/NONE.
  Verified at 100% top-1 (33/33).
- Delegation briefs now carry `route_evidence`; the deliver-time attribution
  assertion (ADR-0003) reads it.
- **Calibration correction:** the confidence FLOOR was set to **13** against the
  golden set, not the "≈6" the plan §4.2 guessed — see plan §9.
- Reversible: additive frontmatter + a standalone script; nothing breaks if the
  tool is removed.

## Alternatives considered

- **Route on `description:` prose only (status quo, richer NLP).** — rejected:
  no deterministic floor, not citable, does not improve consistency, and is
  exactly the model-judgment path RC1 indicts.
- **An LLM-judge router.** — rejected: adds a model call, cost, and
  non-determinism to *every* routing decision; the whole point is a cheap
  deterministic floor.
- **A hardcoded task→agent table inside orchestrator prose.** — rejected: this
  is essentially today's worked-examples list; it is invisible to subagent
  briefs and does not scale as the roster grows.

## Reversibility

`reversible` — additive `routing_triggers` frontmatter plus a new script; removal
restores the prior model-judgment routing with no data migration.

## References

- Plan (source of the decision): `../plans/agent-routing-and-delegation.md`
  §2 (direction), §3 ADR-A, §4.1–§4.3 (schema, scoring, golden set), §6 P0, §9.
- Sibling ADRs: `adr-0002-bounded-delegation-hybrid.md`,
  `adr-0003-enforcement-layering-honesty.md`.
- Catalog: `index.md`.
- Tool: `.claude/agent-lint.py` (seed source
  `integrations/claude-code/agent-lint.py`); golden set `agents/_routes.golden.tsv`.
