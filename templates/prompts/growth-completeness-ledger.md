<!--
Template: prompts/growth-completeness-ledger.md
THE CANONICAL SCHEMA of the growth completeness ledger — the artifact
that makes protocols/grow.md's completeness contract
(grow.completeness-contract) mechanical instead of a matter of judgment.

WHO FILLS IT — the ORCHESTRATION chat, not a spawned worker. It is the
proof, produced before growth is declared done and carried in the
delivery block, that growth reached full depth: every knowledge
collection in the unified docs/graph/ shape is either COVERED to the
depth its evidence supports, or ABSENT because the source genuinely has
no such evidence, or UNKNOWN with a named blocker. A collection may not
be left blank, and "template files exist" is never COVERED.

WHERE IT LIVES — a seed organ, not a plant organ. Like the evidence
ledger it is growth-time feedstock, transient to a grow/adopt run,
written to the plant's gitignored seed-adjacent scratch, NEVER to
docs/graph/:

    .cypress/growth/completeness-ledger.md

Discipline: protocols/grow.md (grow.completeness-contract — the rule,
the no-early-stop clause, the Phase 6 audit that reads this ledger, and
the instruction to include it in the growth delivery).
-->

# Growth completeness ledger — {{plant name}}

One row per knowledge collection in the unified `docs/graph/` shape. Status is
exactly one of:

- **COVERED** — authored to the full depth the evidence supports. Give the count
  of nodes/leaves authored and the strongest source `path`(s) they cite.
- **ABSENT** — the source genuinely has no such evidence. Give the reason and the
  `path`s that were searched to establish the absence. (A real absence is a fact.)
- **UNKNOWN** — a blocker (unreachable source, a two-round non-converging
  `recover` finding, an evidence gap the scouts could not close) prevents
  coverage. Name the blocker. This is the ONLY legitimate way a collection stays
  uncovered, and it ships reported, never silent.

`ran out of context`, `seemed enough`, `templates are present`, and `common
cases done` are NOT statuses — they are the failure the contract forbids.

| Collection                     | Status | Nodes/leaves | Strongest source paths / reason / blocker |
|--------------------------------|--------|--------------|-------------------------------------------|
| root node (governed project)   |        |              |                                           |
| subsystem / capability nodes   |        |              |                                           |
| stack / cross-cutting nodes    |        |              |                                           |
| Tier-1 router (index.md)       |        |              |                                           |
| product/                       |        |              |                                           |
| architecture/                  |        |              |                                           |
| api/                           |        |              |                                           |
| data/                          |        |              |                                           |
| libraries/ (index + rich pages)|        |              |                                           |
| sources/                       |        |              |                                           |
| legal/ (only if in scope)      |        |              |                                           |
| prompts/                       |        |              |                                           |
| evaluations/                   |        |              |                                           |
| runbooks/verification.md       |        |              |                                           |
| plans/grill.md                 |        |              |                                           |
| specs/ (index; formalized only from real observables) |  |     |                                           |
| decisions/ (index; ADRs only from shown decisions)    |  |     |                                           |
| best-practices/                |        |              |                                           |
| changelog.md                   |        |              |                                           |
| project-specific agent(s)      |        |              |                                           |

Growth is done ONLY when every row is COVERED or ABSENT (or a named UNKNOWN),
Phase 6 independent validation passes against the graph, and the maturity test
at the foot of `docs/graph/protocols/grow.md` is met — against the graph,
never the file tree.
