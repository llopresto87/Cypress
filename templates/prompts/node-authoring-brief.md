<!--
Template: prompts/node-authoring-brief.md
Used: when delegating authoring of one or more knowledge-graph nodes
(or wiki pages) to a capable sub-agent, with the linter's rules stated
as constraints so the output passes on the first try.
Model class: opus (the authoring class): node authoring is judgment
work, and a mechanical fill-in produces a node that lies.
Discipline: skills/knowledge-graph, templates/knowledge-graph/_schema.md.
-->

# Node-authoring brief — {{which nodes}}

Write {{N}} knowledge-graph node file(s) for {{project}}. Read
`docs/graph/_schema.md` first for the contract, and {{an existing node}}
as a style exemplar. Execute the graph first; these blocks are your
routing.
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

If you can delegate (for example, spawning `research-scout` to refresh a
source), spawn only from your `delegates_to` allowlist within your depth
cap; outside it, hand back.

Write: {{list the exact file paths; each filename is the id plus `.md`}}.

## Linted rules (a violation fails the build)

1. Frontmatter is the tiny YAML subset: `key: scalar`, or `key:` then
   two-space-indented `  - item` lines. That subset is house style for
   an authored node; the reader also accepts two exceptions, an agent
   node's inline `tools: [a, b]` list and the router's one-level
   `plant:` block, and rejects any other YAML shape.
2. Required keys (the linter checks presence, not order): `id`, `tier`,
   `kind`, `title`, `owns`, `requires`, `load_when`, `est_tokens`.
   `tier: 2`. `repo`, `peers`, `composes`, `libraries`, and `artifacts`
   are optional keys the linter validates only when they are present;
   listing them in the order above is house style, not a gate.
3. **Versions live in `docs/graph/libraries/`**: the body links there,
   and the linter rejects a version number outside inline or fenced
   code.
4. `owns:` fact-keys are prefixed with the node's short name and are
   unique across the whole graph.
5. `requires:` only ids from {{the allowed set}} — minimal (2–4).
   `peers:` only ids from {{the allowed set}}. `composes:` only on an
   `expertise` node and only toward `expertise` nodes — the parent lists
   its specialisations, and each child `requires:` that parent back.
6. Body: the linter hard-fails only above 170 lines — aim for ~150. The
   section order is house style, not a linted rule: "What this is" (2–3
   sentences), "What you must know", "Sharp edges", "Where the code is",
   "Neighbours" (one line per peer: why + when to cross).
7. `est_tokens` ≈ 1.35 × body word count — honest; the linter fails if
   off by >2×.
8. Every `artifacts:` path is relative to `docs/graph/`, resolves there,
   and points to source-backed depth owned by this node.

## FACTS (verbatim: the complete set you write from)

{{Paste the investigation facts for each node here. If a fact is not
supplied, the node says "not recorded".}}

## Return

The file paths written, and any fact you deliberately omitted for
length. Then confirm the linter passes (or report what it flags).
