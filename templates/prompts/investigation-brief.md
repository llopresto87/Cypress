<!--
Template: prompts/investigation-brief.md
Used: when delegating a READ-ONLY investigation of a subsystem to a
sub-agent, to gather facts for a spec, a graph node, or a plan.
Fill the {{PLACEHOLDERS}} and hand the body to the sub-agent.
Discipline: agents/00-orchestrator.md (delegation), skills/knowledge-graph.
-->

# Investigation brief — {{subsystem or area}}

**Model class: sonnet.** This is read-only investigation — no authoring,
no judgment-heavy design.

Investigate {{subsystem / repo / path}} and report **facts only**, for
the purpose of {{authoring a node / writing a spec / planning a change}}.

## Rules (state these to the sub-agent verbatim)

- **Execute the graph first.** The route-hook does not fire for you.
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
- **Cite the router.** This brief was selected by `agent-lint --route`; the
  ranked line and confidence band that picked you are: {{paste the `agent-lint
  --route` line + band}}. Echo it back in `route_evidence`, and if you were
  routed here at LOW/NONE confidence say so — you may be the wrong specialist.
- **End with a handback.** Close your turn with the payload from
  `docs/graph/templates/prompts/handback-payload.md`: `produced_by: {{you}}`,
  `in_domain_work_done` with paths, `route_evidence`, and — at any
  out-of-domain boundary — `recommended_next` naming the specialist. You are a
  read-only leaf: name the next specialist and STOP; do not do that work.
- **Do NOT read every file.** Sample intelligently: {{which manifests,
  entry points, config files to prioritize}}. Confirm a path with
  `ls`/`grep`; do not bulk-read to "get oriented."
- **Report facts with evidence.** Every claim carries a concrete file
  path (and line where it matters) and an exact value (version, port,
  name) — not a paraphrase.
- **Say "not found" rather than guessing.** Accuracy matters more than
  completeness — a gap you name is useful (the no-fabrication rule is
  GRAPH DISCIPLINE 4, above).
- **Read-only.** Do not create, edit, or run anything that mutates
  state.
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

A structured, terse report. Cite paths. Flag every "not found". End
with anything you deliberately omitted for length, so the caller can
ask for it.
