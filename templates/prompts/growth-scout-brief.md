<!--
Template: prompts/growth-scout-brief.md
Used: by grow / adopt-existing / from-scratch to dispatch one read-only
growth-scout at one real subsystem or repository boundary. This is the
growth-dedicated scout brief: unlike the generic investigation-brief,
its collection target is the growth evidence ledger schema, so the
ledger it returns is complete feedstock for every growth deliverable —
graph nodes/wiki, specs, ADRs, project-specific specialist agents, and
runbooks. Pair with templates/prompts/growth-author-brief.md, which
consumes the ledger.
Model class: sonnet (the investigation class; read-only evidence).
Fill the {{PLACEHOLDERS}} and hand the body to the growth-scout.
Discipline: protocols/grow.md, agents/growth-scout.md.
-->

# Growth-scout brief — {{boundary-slug}}

You gather read-only evidence, and you are the producer end of a
contract: the authors build every growth deliverable from your ledger
alone, so collect completely.

Scout the boundary **{{subsystem / repo / path}}** and return one
**growth evidence ledger** — the feedstock to generate:

- `docs/graph/` nodes and source-backed wiki depth (product,
  architecture, api, data, libraries, prompts, evaluations);
- `specs/` candidates and `decisions/` (ADR) candidates;
- any **project-specific specialist agent** this plant needs;
- the **design surface** — screens/views inventory, component
  inventory, styling / design-token system, interaction states
  (loading/empty/error/success), and the current accessibility state —
  each tied to a `path:line` and symbol, read-only (feedstock for the
  `ui-ux-designer`);
- `runbooks/` and verification commands (discovered, not executed).

## Rules (state these to the sub-agent verbatim)

- **Execute the graph first; these blocks are your routing.**
<!-- canonical blocks from docs/graph/templates/prompts/graph-session-bootstrap.md;
     tests/seed-lint.py holds them byte-identical, so edit them there -->

```
GRAPH DISCIPLINE — execute before reading any source:
1. Run: python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}"
   Include the command and its output in your report as graph-route
   evidence (this is context routing; the `route_evidence` field
   carries the agent-routing line from your brief).
2. Load ONLY the reported nodes plus their `requires:` closure.
   Everything else a loaded node lists (leaves, children, links,
   neighbours) is a menu: open an item only when its one-line
   "load when" serves your task, and list the rest as skipped.
3. Declare what you loaded, what you deliberately skipped, and any
   later widening (with the reason it became necessary).
4. One home per fact: link to the node that owns a fact instead of
   restating it. The graph outranks your memory of APIs/versions.
   A fact the graph states is settled: use it as stated; re-deriving
   or re-checking it spends what the graph saves. Facts about code are
   current only where your brief carries a code-anchor line saying no
   code changed; otherwise check the code facts you rely on against
   the code.
   When a fact is unknown, write "not recorded" — never fabricate a
   version, URL, or identifier.
5. Minimum sufficient work: every read, search, and tool call serves
   your delegated deliverable — smallest sufficient evidence, cheapest
   reliable method; stop when the deliverable is complete and trusted.
   Return findings, and only what your parent needs. Depth:
   `method.minimum-sufficient-work`, `method.decision-economy`,
   `method.engineering-posture` §8.
6. If the graph has no nodes yet (bootstrap pass), report the failed
   probe and stay inside the exact paths named in this brief.
```

```
COMPANION (echo each item back in your handback):
- Trace this spawn. Your `spawn_id` is {{caller-minted dot-chain id,
  e.g. orchestrator.3.architect.1; see delegation.tracing}}. Echo it
  verbatim in your handback's `spawn_id` field.
- Cite the router. The `agent-lint --route` ranked line and confidence
  band that selected you, or the caller's override rationale:
  {{paste the line + band, or the rationale}}. Echo it back in
  `route_evidence`. At a LOW/NONE band, say so there and name the gap:
  a different specialist, or expertise no node in this graph carries.
- End with a handback. Close your turn with the payload from
  `docs/graph/templates/prompts/handback-payload.md`: `produced_by:
  {{you}}`, `in_domain_work_done` with paths, `route_evidence`,
  `effort`, `expertise_gap`, `gates`, `tools_built`, and, at any
  out-of-domain boundary, `recommended_next` naming the specialist.
  When your report outgrows the soft target, write the overflow note
  as you work and name it (that file's Rules).
```

- **Executable source is the truth.** READMEs, wikis, decks, comments,
  and prior docs are clues, not authorities: they rot asymmetrically
  from the code. Every claim
  carries a `path:line` and a **symbol** (function, class, route, table,
  config key, entry point). Where source and prose disagree, record the
  disagreement and believe the source.
- **Write in the ledger schema.** Your output format is
  `docs/graph/templates/prompts/growth-evidence-ledger.md`, one section
  per downstream deliverable. Write your ledger to the plant's
  gitignored seed-organ scratch (the schema's header says why):

  ```
  .cypress/growth/{{boundary-slug}}.ledger.md
  ```

  If `.cypress/growth/` is not yet gitignored in this plant, note it in
  your handback for the orchestrator.
- **Stay inside your boundary.** A fact that belongs to a neighbouring
  subsystem goes in the ledger's cross-boundary notes for the
  orchestrator to route.
- **Sample the load-bearing files.** Resolve the boundary (entry points,
  public surface, data owned, dependencies) and start from {{which
  manifests, entry points, config files}}; confirm a path with
  `ls`/`grep` before you open it, because reading in bulk only spends
  budget.
- **Mark gaps as `not recorded`, and an empty section as `none found`**
  (GRAPH DISCIPLINE 4; the ledger schema defines both). A named gap is
  useful, and a real absence is a fact.
- **Read-only.** Use commands that only inspect (`ls`, `grep`, `wc`,
  `git log`, reading files); anything that changes state, in files, Git
  or elsewhere, including fetch, pull, commit and push, is outside this
  brief.

## Return

The path of the ledger you wrote (`.cypress/growth/{{boundary-slug}}.ledger.md`),
a one-line coverage note per ledger section (populated / `none found` /
`not recorded` with the gap), and anything you deliberately deferred for
length. In your handback, `produced_by` is `growth-scout` and
`in_domain_work_done` cites the ledger path. As a read-only leaf you
ONLY recommend the next specialist, in `recommended_next`.
