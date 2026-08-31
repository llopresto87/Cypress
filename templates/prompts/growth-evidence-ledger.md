<!--
Template: prompts/growth-evidence-ledger.md
THE CANONICAL SCHEMA of the growth evidence ledger — the one structured
artifact that passes between a growth-scout (producer) and a growth
author (consumer). A scout fills ONE ledger per boundary; the authors
read it and build every growth deliverable from its cited claims,
instead of re-investigating source from scratch.

WHERE IT LIVES — a seed organ, not a plant organ. The ledger is
growth-time feedstock, transient to a grow/adopt run. It is written to
the PLANT's gitignored seed-adjacent scratch, NEVER to docs/graph/
(which is permanent plant knowledge):

    .cypress/growth/<boundary-slug>.ledger.md

Growth ensures `.cypress/growth/` is gitignored in the plant (the
plant-owned `.cypress/seed.json` stamp stays tracked; this transient
does not). After delivery the plant keeps docs/graph and may discard
`.cypress/growth/` — the harvest/graft/grow machinery is a seed organ
the living plant does not carry.

Discipline: protocols/grow.md, agents/growth-scout.md (producer),
agents/growth-orchestrator.md + templates/prompts/growth-author-brief.md
(consumers).
-->

# Growth evidence ledger — {{boundary-slug}}

One boundary, one ledger. Every claim is a fact **from executable
source**, anchored to `path:line` and a **symbol** (function, class,
route, table, config key, entry point). Prose/READMEs are clues until
corroborated; where source and prose disagree, record the disagreement
and believe the source. A fact you cannot establish from source is
written `not recorded` with the evidence a follow-up would need — never
guessed. Terse claims, not prose.

Each section names the **downstream deliverable** it feeds, so the scout
knows *why* it collects each fact and the author knows *where* each fact
goes. A section with no evidence says `none found` (a real absence is a
fact); it is never padded to look populated.

## 0 — Boundary & provenance  → root/subsystem node, changelog

- **Boundary**: {{subsystem / repo / path}} and its edges (what it is,
  what it is not).
- **Provenance** (read-only, do not mutate Git): repo path, current
  branch, HEAD short-sha, worktree clean/dirty, stack/manifests.
- **Scout & date**: `produced_by: growth-scout`, run date.

## 1 — Structure & entry points  → architecture/ nodes + components

- Bootstrap, entry points, packages/services, layering, and the
  responsibilities each owns. `path:line` + symbol per claim.

## 2 — Capabilities, actors & flows  → product/ nodes

- Each capability the boundary provides, the actor it serves, and the
  code that implements it (`path:line` + symbol). Observed behavior,
  not aspiration.

## 3 — Contracts (api / messages / jobs)  → api/ nodes

- Inbound routes/messages/jobs and outbound integrations: method, path
  or topic, handler symbol, and the source location. Protocol per edge.

## 4 — Data & entities  → data/ nodes + data-contracts

- Entities/tables/documents owned, constraints, enums, migrations,
  persistence, lineage, and any privacy-sensitive fields. Symbol + path;
  put version-pinned facts here with their lockfile/manifest source.

## 5 — Dependencies  → libraries/ index + rich pages

- Every direct dependency with evidence of *actual use* (import site
  `path:line`), lock/manifest pin location, and whether it is
  architecturally significant / cross-cutting / security- or
  operations-critical (those earn a rich library page; the rest, an
  index line). Read pins from the tree, never from memory.

## 6 — Prompts & evaluations  → prompts/ + evaluations/ nodes

- AI contracts, call sites, datasets, rubrics, gates, and failure modes,
  each tied to source. `none found` if the boundary has no AI surface.

## 7 — Spec-worthy behaviors  → specs/ feedstock (§3.1 gate)

- Behaviors that carry enough risk/contract weight to deserve an
  executable spec: the behavior in one line, the code that realizes it
  (`path:line` + symbol), and the observable it would assert. This is a
  *candidate list* for the author to formalize — not an authored spec.

## 8 — ADR-worthy decisions  → decisions/ feedstock

- Decisions **visible in the source** (a chosen library over an
  obvious alternative, a boundary drawn deliberately, a config default
  with consequences): decision, evidence path, alternatives/consequences
  the code reveals. Never infer rationale the source does not show —
  mark unknown rationale `not recorded`. A candidate list, not an
  authored ADR.

## 9 — Specialist-agent signals  → project-specific expert agents

- Evidence about what *project-specific expertise* a plant needs beyond
  the base roster: dominant domain language, unusual stack/runtime, a
  high-risk surface (auth, payments, PII, migrations), or a recurring
  task shape. Each signal cites the source that motivates it. The author
  decides whether a signal warrants a custom agent; the scout only
  supplies the grounded evidence.

## 10 — Operational evidence  → runbooks/ + verification (discovered)

- Exact commands, test invocations, CI gates, build/deploy/rollback
  descriptors, and observability hooks, each with its source location.
  Everything here is **discovered, not executed** — the author labels it
  so. Never claim a command passes.

## 11 — Sharp edges  → wherever the owning fact lives

- Surprising coupling, undocumented invariant, config that silently
  changes behavior — the facts the next agent most needs and the code
  least advertises. `path:line` + what makes it sharp.

## 12 — Uncertainties & cross-boundary notes

- **Uncertainties**: what could not be established from source, each
  with the evidence a follow-up scout would need. `not recorded`, never
  a guess.
- **Cross-boundary notes**: facts that belong to a neighbouring
  boundary — for the orchestrator to route, not for this scout to chase.

## Handback

The scout ends its turn with the payload from
`docs/graph/templates/prompts/handback-payload.md` (`produced_by: growth-scout`,
`in_domain_work_done` citing the ledger path, `route_evidence`, `gates`,
`tools_built`), and names the ledger file it wrote.
