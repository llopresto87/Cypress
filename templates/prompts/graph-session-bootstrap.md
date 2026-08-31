<!--
Template: prompts/graph-session-bootstrap.md
THE CANONICAL HOME of the graph-session discipline. Every delegation
brief EMBEDS the block below verbatim (hooks do not reach subagents, so
the brief is the only enforcement that crosses the boundary). Every
other seed file — kernel, agents, protocols, skills — REFERENCES this
file instead of paraphrasing the discipline; a paraphrase is a second
home for the same rule, and duplicated rules rot asymmetrically.
Fill {{PLACEHOLDERS}} when embedding.
-->

# Graph-session bootstrap (embed verbatim in every delegation brief)

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

## Companion requirements (also carried by every brief)

- **Routing evidence** — paste the `agent-lint --route` ranked line and
  confidence band that selected the specialist (or the override
  rationale). The worker echoes it back as `route_evidence`.
- **Handback** — the worker ends its turn with the payload from
  `docs/graph/templates/prompts/handback-payload.md` (`produced_by`,
  `in_domain_work_done`, `route_evidence`, `gates`, `tools_built`).

## Why embedding, not referencing, at the delegation boundary

Subagents start with a clean context and no hooks fire for them. A
reference the worker may never resolve is not enforcement; the embedded
block is. This is the one deliberate exception to one-home-per-rule:
the *runtime brief* embeds; every *static seed file* references.
