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
- **An agent-operations system is evidence.** Agent charters, harness
  hooks, instruction files and lesson or memory logs already in the tree
  are inventoried, not waved off as stale or as a bulk read: each hook
  with the event it fires on and what it blocks, each log entry with its
  date and the paths it names. Outside your boundary, name the system in
  the cross-boundary notes so the orchestrator assigns it a scout.
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
length. In your handback, `in_domain_work_done` cites the ledger path. As a read-only leaf you
ONLY recommend the next specialist, in `recommended_next`.
