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
1. Run: python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}" --role {{role}}
   Report it in `graph_route:` as ids, never the router's output.
2. Load ONLY the reported nodes plus their `requires:` closure.
   Everything else a loaded node lists (leaves, children, links,
   neighbours) is a menu: open an item only when its one-line
   "load when" serves your task, and list the rest as skipped.
3. Before reading the files you will touch, check that each stack
   element they use (extension, path, manifest, lockfile) and their
   area has an `expertise.*` node, owning node or `libraries/` page in
   the route; for each one missing, run `--plan "<that element>"` and
   load what it reports. Declare in `graph_route:` what you loaded,
   skipped, and widened (with the reason).
4. Link to the node that owns a fact; do not restate it. The graph
   outranks your memory of APIs and versions. A fact the graph states
   is settled: use it as stated; re-deriving or re-checking it spends
   what the graph saves. Facts about code are current only where your
   brief carries a code-anchor line saying no code changed; otherwise
   check the code facts you rely on against the code. An unknown fact
   is "not recorded": never invent a version, URL or identifier.
5. Every read, search and tool call serves the deliverable; stop when
   it is complete and trusted. Read a spec by contract:
   `python3 docs/graph/spec-lint.py --slice --refs SLUG...`, then open
   only the §6/§7 headings it cites. Return only what your parent
   needs (`method.minimum-sufficient-work`).
6. Leave shared git state alone: `git stash`, `checkout`, `restore`,
   `reset` and `clean` move other writers' uncommitted files. Take a
   baseline by copying the file or `git show HEAD:<path>`
   (`delegation.wave-baseline`).
7. No graph nodes yet (bootstrap pass): report the failed probe and
   stay inside the paths this brief names.
```

```
COMPANION:
- Routed by: {{the protocol phase, the agent-lint --route line and band,
  or the override rationale}}. brief.py logged it with your spawn_id, role
  and effort, so your handback starts at `status:`. At a LOW/NONE band,
  name the gap in `out_of_domain_needed`: the fitting specialist, or the
  expertise the graph still needs.
- End your turn with the HANDBACK payload; at an out-of-domain boundary
  name the specialist in `recommended_next`. Past the soft target, write
  the overflow note as you work and name it (handback-payload.md, Rules).
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
