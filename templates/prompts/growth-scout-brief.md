<!--
Template: prompts/growth-scout-brief.md
Used: by grow / adopt-existing / from-scratch to dispatch ONE read-only
growth-scout at ONE real subsystem or repository boundary. This is the
GROWTH-DEDICATED scout brief: unlike the generic investigation-brief,
its collection target IS the growth evidence ledger schema, so the
ledger it returns is complete feedstock for every growth deliverable —
graph nodes/wiki, specs, ADRs, project-specific specialist agents, and
runbooks. Pair with templates/prompts/growth-author-brief.md, which
consumes the ledger.
Fill the {{PLACEHOLDERS}} and hand the body to the growth-scout.
Discipline: protocols/grow.md, agents/growth-scout.md.
-->

# Growth-scout brief — {{boundary-slug}}

**Model class: sonnet.** Read-only evidence gathering — no authoring, no
design judgment. You are the producer end of a contract: the authors
build every growth deliverable from your ledger, so what you fail to
collect, they cannot write (they do not re-investigate source).

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

- **Executable source is the truth.** READMEs, wikis, decks, comments,
  and prior docs are clues, not authorities — they rot asymmetrically
  from the code. Every claim carries a `path:line` and a **symbol**
  (function, class, route, table, config key, entry point). Where source
  and prose disagree, record the disagreement and believe the source.
- **Fill the ledger schema, do not improvise a format.** Your output
  format is `docs/graph/templates/prompts/growth-evidence-ledger.md` — one section
  per downstream deliverable. Write your ledger to the plant's gitignored
  seed-organ scratch, NOT to `docs/graph/`:

  ```
  .cypress/growth/{{boundary-slug}}.ledger.md
  ```

  If `.cypress/growth/` is not yet gitignored in this plant, note it in
  your handback for the orchestrator (the ledger is a growth-time seed
  organ; the plant does not carry it).
- **Stay inside your boundary.** A fact that belongs to a neighbouring
  subsystem goes in the ledger's cross-boundary notes for the
  orchestrator to route — you do not widen scope to chase it.
- **Do NOT bulk-read.** Resolve the boundary — entry points, public
  surface, data owned, dependencies — and sample the load-bearing files.
  Prioritize: {{which manifests, entry points, config files}}. Confirm a
  path with `ls`/`grep` before reading.
- **Say `not recorded` rather than guessing.** A named gap is useful; a
  confident invention is a trap (the no-fabrication rule is GRAPH
  DISCIPLINE 4, above). `none found` for an empty section is itself a
  fact — never pad a section to look populated.
- **Read-only.** `Bash` only for read-only inspection (`ls`, `git log`,
  `wc`). Do not create, edit, or run anything that mutates state, and do
  not fetch/pull/commit/push Git.
- **Cite the router.** This brief was selected by `agent-lint --route`;
  the ranked line and confidence band that picked you are: {{paste the
  `agent-lint --route` line + band}}. Echo it back in `route_evidence`.

## Return

The path of the ledger you wrote (`.cypress/growth/{{boundary-slug}}.ledger.md`),
a one-line coverage note per ledger section (populated / `none found` /
`not recorded` with the gap), and anything you deliberately deferred for
length. End your turn with the payload from
`docs/graph/templates/prompts/handback-payload.md` (`produced_by: growth-scout`,
`in_domain_work_done` citing the ledger path, `route_evidence`). You are
a read-only leaf: at an out-of-domain boundary, name the next specialist
in `recommended_next` and STOP — a missing `produced_by` is a
deliver-time BLOCK.
