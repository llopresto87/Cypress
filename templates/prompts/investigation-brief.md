<!--
Template: prompts/investigation-brief.md
Used: when delegating a read-only investigation of a subsystem to a
sub-agent, to gather facts for a spec, a graph node, or a plan.
Model class: sonnet (the investigation class; read-only evidence).
Fill the {{PLACEHOLDERS}} and hand the body to the sub-agent.
Discipline: agents/00-orchestrator.md (delegation), skills/knowledge-graph.
-->

# Investigation brief — {{subsystem or area}}

Investigate {{subsystem / repo / path}} and report **facts only**, read-only,
for the purpose of {{authoring a node / writing a spec / planning a change}}.

## Rules (state these to the sub-agent verbatim)

- **Execute the graph first; these blocks are your routing.**
<!-- canonical blocks from docs/graph/templates/prompts/graph-session-bootstrap.md;
     tests/seed-lint.py holds them byte-identical, so edit them there -->

```
GRAPH DISCIPLINE — execute before reading any source:
1. Run: python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}"
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

- **You are a read-only leaf.** At an out-of-domain boundary you ONLY
  recommend the next specialist; the work stays with them.
- **Sample the load-bearing files.** Start from {{which manifests, entry
  points, config files to prioritize}}, and confirm a path with
  `ls`/`grep` before you open it; the graph gives you your bearings, so
  reading in bulk only spends budget.
- **Report facts with evidence.** Every claim carries a concrete file
  path (and line where it matters) and an exact value (version, port,
  name) — not a paraphrase.
- **Name the gap instead of guessing.** Write "not recorded" for a fact
  you could not establish, and "none found" for an absence you checked,
  with what you searched. Accuracy matters more than completeness: a gap
  you name is useful (the no-fabrication rule is GRAPH DISCIPLINE 4,
  above).
- **If what this brief assumes exists does not, say so and stop.** A
  brief that asks you to restore something from history, or to find
  where something is set, assumes that it exists or once did. When the
  search shows it does not, or never did, report that result with what
  you searched (every branch, deleted and renamed paths, a content
  search over history) and stop. Hand back the negative result itself:
  an invention in its place reads like a recovery.
- **Read-only.** Use commands that only inspect (`ls`, `grep`, `wc`,
  `git log`, reading files); anything that changes state, in files, Git
  or elsewhere, is outside this brief.
- Be terse. Bullets and tables. This feeds a system prompt / a node, so
  precision beats prose.

## Report these, concretely

1. {{Structure: layout, main abstractions, conventions — naming, error
   handling, layering.}}
2. {{Versions / pins / config that other work depends on.}}
3. {{External edges: what it calls, what calls it, over what protocol.}}
4. {{Data it owns: entities/tables/documents, constraints, enums.}}
5. {{Tests, gates, CI — what exists and what is absent.}}
6. {{Anything surprising or non-standard a maintainer must know.}}

## Return

A structured, terse report. Cite paths. Flag every "not recorded" and
"none found". End
with anything you deliberately omitted for length, so the caller can
ask for it.
