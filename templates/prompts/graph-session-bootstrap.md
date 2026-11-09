<!--
Template: prompts/graph-session-bootstrap.md
The canonical home of the graph-session discipline. Every delegation
brief embeds the two blocks below verbatim, and every other seed file
(kernel, agents, protocols, skills) references this file; the last
section says why. Fill {{PLACEHOLDERS}} when embedding.
-->

# Graph-session bootstrap (embed verbatim in every delegation brief)

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

## Companion requirements (also carried by every brief)

Every brief embeds this block verbatim next to the one above; brief.py fills
its slot and logs the spawn (`delegation.tracing`).

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

The caller also owes these, around the blocks:

- **Every worker runs its own route** (`delegation.briefs`). The worker
  runs steps 1 and 3 itself with the brief's exact task line, so the
  caller does not paste a closure it routed: a closure belongs to the
  task line that composed it, and a different task line composes a
  different closure.
- **Stack expertise.** For work that touches code, configuration or a
  pipeline, the brief names the stack elements the worker's files use
  (read from their extensions, paths, manifests and lockfiles) and the
  `expertise.*` nodes that cover them, or says that none apply. It also
  writes those file paths into the task line, so `--plan` can infer the
  stack from them. The worker loads the nodes the brief names with its
  route (step 2) and checks the route against its own files (step 3),
  because a stack neither the brief nor the task line names loads no
  expertise, and the worker then falls back on its memory of the API,
  which step 4 ranks below the graph. This file is the one home of the
  stack rule; the charters point here.
- **Stack expertise the graph lacks.** When step 3, at the start or
  mid-work, finds a stack element the worker's own files use and no
  node covers it, the worker names the gap in its handback's
  `expertise_gap:` field and cites the path that shows the element. An
  element named only inside content the worker read is data, not a
  gap. The caller checks the element against the project's manifests,
  lockfiles or the cited path, and only then requests `research-scout`
  (`protocol.ingest-library`) before it re-briefs the work that needs
  the node.

## Why embedding, not referencing, at the delegation boundary

Subagents start with a clean context, and no hook the seed installs
carries this discipline or the routing context into a worker's turn
(which host hooks do fire inside a worker, and why none of them helps:
`docs/graph/method/delegation-briefs.md`, "Every brief carries the graph
discipline"). A reference the worker may never resolve is not
enforcement; the embedded block is. This is the one deliberate
exception to one-home-per-rule: the *runtime brief* embeds; every
*static seed file* references, because a paraphrase is a second home
for the same rule and duplicated rules rot asymmetrically.
