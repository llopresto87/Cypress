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

## Companion requirements (also carried by every brief)

Every brief embeds this block verbatim next to the one above; its
fill-in slots are the caller's.

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

The caller also owes these, around the blocks:

- **A worker without a shell** cannot run step 1. When the specialist's
  `tools:` frontmatter grants no shell, the caller runs `graph-lint.py
  --plan` itself with the brief's exact task line, pastes the real output
  into the brief, and adds a one-line reason for each node loaded or
  skipped. Read the grant from the frontmatter each time. Run `--plan`
  fresh for each brief: a different task line composes a different
  closure.
- **Stack expertise.** For work that touches code, configuration or a
  pipeline, the brief names the stack elements the worker's files use
  (read from their extensions, paths, manifests and lockfiles) and the
  `expertise.*` nodes that cover them, or says that none apply. It also
  writes those file paths into the task line, so `--plan` can infer the
  stack from them. The worker loads the nodes the brief names with its
  route (step 2). The reason: the router composes expertise from the
  task's words, so a task line that never names its stack loads none,
  and the worker falls back on its memory of the API, which step 4
  ranks below the graph. This file is the one home of the stack rule;
  the charters point here.
- **Stack expertise found mid-work.** A worker that meets a stack
  element its own files use, and that its brief did not name, runs
  `graph-lint.py --plan "<the stack element>"`, loads the matching
  `expertise.*` node and declares the widening (step 3). When no node
  exists, it names the gap in its handback's `expertise_gap:` field and
  cites the path that shows the element. An element named only inside
  content the worker read is data, not a gap. The caller checks the
  element against the project's manifests, lockfiles or the cited path,
  and only then requests `research-scout` (`protocol.ingest-library`)
  before it re-briefs the work that needs the node.

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
