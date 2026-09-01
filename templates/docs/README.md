# Unified project knowledge graph

`docs/graph/` is the project's single knowledge system. It combines:

- **progressive discovery** — start at the router, load only matching
  nodes, follow required edges, then open named leaves;
- **a graph** — nodes own facts and connect dependencies, peers, and
  detailed artifacts explicitly;
- **an LLM wiki** — detailed, source-backed project and dependency
  knowledge lives in graph leaf collections.

No parallel documentation hierarchy is authoritative. Existing prose
outside this graph is evidence to corroborate against executable source,
then link or ingest here without duplicating facts.

## Map

- `index.md` — Tier-1 context router. **Start here on every task.**
- `nodes/` — Tier-2 owned facts and routing edges.
- `_schema.md` + `graph-lint.py` — graph contract and validator.
- `plans/grill.md` — the plan-of-record for active delivery work.
- `specs/` — executable specifications (one per significant behavior).
- `decisions/` — Architecture Decision Records.
- `libraries/` — the LLM-maintained wiki: one page per dependency.
- `sources/` — original and normalized external sources.
- `runbooks/` — operational procedures (local dev, verification,
  release, rollback, incident).
- `tools/` — catalog of durable, reusable tools the project has built;
  one card per tool (interface, invocation, tests), indexed by `index.md`.
- `best-practices/` — project-local synthesis of best practices.
- `product/` — user-facing requirements and flows.
- `architecture/` — diagrams and architecture deep dives.
- `api/` — public/internal API references.
- `data/` — data contracts and lineage.
- `evaluations/` — evaluation plans and rubrics for AI behavior.
- `design/` — implementable interface/interaction design specs
  (`ui-ux-designer`), mapped to spec §3/§9.
- `prompts/` — versioned prompts and prompt contracts.
- `changelog.md` — meaningful project changes.

## Conventions

- Section numbers in `grill.md` and spec files are stable: agents and
  tooling index into them. Do not renumber.
- ADRs are numbered monotonically: `adr-NNNN-short-slug.md`. Never
  reuse a number; supersede instead.
- Specs are numbered monotonically: `SPEC-NNNN-short-slug.md`.
- Wiki pages are `<library-name>.md` and indexed by
  `libraries/index.md`.
- Every doc names its neighbors (links to grill section, spec, ADRs,
  wiki pages, runbook commands).

## How to add to this tree

Use the protocols. All destinations below are relative to this graph:

- `specify` → `specs/`
- `grill` → `plans/grill.md`
- `ingest-library` → `libraries/` + `sources/`
- `canonize` close-out → `tools/` (docs-librarian cards +
  `tools/index.md`), applying the `toolcraft` doctrine; `toolcraft` is
  never entered as a command of its own
- Architect → `decisions/` (ADRs)
- Product → `product/`
- Ui-ux-designer → `design/`
- Tester → `evaluations/`, `runbooks/verification.md`
- Reliability → `runbooks/`
- Security → `decisions/` (threat models), `runbooks/incident-response.md`

After adding a leaf, connect it from the owning node with an
`artifacts:` edge (or `libraries:` for a dependency wiki page).
