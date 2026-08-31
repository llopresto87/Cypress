<!--
Template: prompts/node-authoring-brief.md
Used: when delegating authoring of one or more knowledge-graph nodes
(or wiki pages) to a capable sub-agent, with the linter's rules stated
as hard constraints so the output passes on the first try.
Author these with a capable model — node authoring is high-level work,
not a mechanical fill-in.
Discipline: skills/knowledge-graph, templates/knowledge-graph/_schema.md.
-->

# Node-authoring brief — {{which nodes}}

**Model class: opus.** Node authoring is high-level work — a mechanical
fill-in produces a node that lies.

Write {{N}} knowledge-graph node file(s) for {{project}}. Read
`docs/graph/_schema.md` FIRST for the contract, and {{an existing node}}
as a style exemplar. The route-hook does not fire for you.
<!-- canonical block from docs/graph/templates/prompts/graph-session-bootstrap.md;
     byte-identity enforced by tests/seed-lint.py — edit it THERE -->

```
GRAPH DISCIPLINE — execute before reading any source:
1. Run: python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}"
   Include the command and its output in your report as graph-route
   evidence (context routing — NOT the `route_evidence` field, which
   carries the agent-routing line from your brief).
2. Load ONLY the reported nodes plus their `requires:` closure.
3. Declare what you loaded, what you deliberately skipped, and any
   later widening (with the reason it became necessary).
4. One home per fact: never duplicate a fact the graph owns — link to
   its owning node. The graph outranks your memory of APIs/versions.
   When a fact is unknown, write "not recorded" — never fabricate a
   version, URL, or identifier.
5. Minimum sufficient work: every read, search, and tool call serves
   your delegated deliverable — smallest sufficient evidence, cheapest
   reliable method; stop when the deliverable is complete and trusted.
   Return findings, not raw dumps; produce nothing your parent does
   not need. Depth: `docs/graph/method/engineering-posture.md` §5–§8.
6. If the graph has no nodes yet (bootstrap pass), report the failed
   probe and stay inside the exact paths named in this brief.
```

If the first node set is not routable yet, use only the exact
schema/evidence paths supplied here.

This brief was selected by `agent-lint --route`; the ranked line and
confidence band that picked you are: {{paste the `agent-lint --route` line +
band}} — echo it back in `route_evidence`. If you can delegate (e.g. spawning
`research-scout` to refresh a source), spawn only from your `delegates_to`
allowlist within your depth cap; otherwise STOP and hand back. Close your turn
with the payload from `docs/graph/templates/prompts/handback-payload.md`:
`produced_by: {{you}}`, `in_domain_work_done` with paths, `route_evidence`,
and — at any out-of-domain boundary — `recommended_next` naming the specialist.

Write: {{list the exact file paths — filename MUST equal the id + ".md"}}.

## HARD RULES (a linter enforces these; violations fail the build)

1. Frontmatter is the tiny YAML subset only: `key: scalar`, or `key:`
   then two-space-indented `  - item` lines. No nested maps, no inline
   `[a, b]` lists.
2. Required keys, in order: `id`, `tier`, `kind`, `title`, `repo`
   (optional), `owns`, `requires`, `peers`, `libraries` (may be empty),
   `artifacts` (may be empty), `load_when`, `est_tokens`. `tier: 2`.
3. **No version numbers in the body** — the linter rejects them outside
   inline/`fenced` code. Versions live in `docs/graph/libraries/`; link
   instead.
4. `owns:` fact-keys are prefixed with the node's short name and are
   **unique across the whole graph**.
5. `requires:` only ids from {{the allowed set}} — minimal (2–4).
   `peers:` only ids from {{the allowed set}}.
6. Body ≤ 150 lines, sections in order: "What this is" (2–3 sentences),
   "What you must know", "Sharp edges", "Where the code is",
   "Neighbours" (one line per peer: why + when to cross).
7. `est_tokens` ≈ 1.35 × body word count — honest; the linter fails if
   off by >2×.
8. Every `artifacts:` path is relative to `docs/graph/`, resolves there,
   and points to source-backed depth owned by this node.

## FACTS (verbatim — do not invent beyond these)

{{Paste the investigation facts for each node here. If a fact is not
supplied, the node says "not recorded" — the sub-agent does not fill
gaps from memory.}}

## Return

The file paths written, and any fact you deliberately omitted for
length. Then confirm the linter passes (or report what it flags).
