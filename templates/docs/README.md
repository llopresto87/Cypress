# Unified project knowledge graph

`docs/graph/` is the project's single knowledge system. It combines:

- **progressive discovery**: start at the router, load only matching
  nodes, follow required edges, then open named leaves;
- **a graph**: nodes own facts and connect dependencies, peers, and
  detailed artifacts explicitly;
- **an LLM wiki**: detailed, source-backed project and dependency
  knowledge lives in graph leaf collections.

This graph is the only authoritative documentation. Prose outside it is
evidence: corroborate it against executable source, then link or ingest
it here, one home per fact.

## Map

- `index.md`: Tier-1 context router. **Start here on every task.**
- `nodes/`: Tier-2 owned facts and routing edges.
- `_schema.md` + `graph-lint.py`: graph contract and validator.
- `plans/grill.md`: the plan-of-record for active delivery work.
- `plans/sessions/`: dated session records, the working state one
  session hands to the next (`_session-record.template.md` is the form).
- `specs/`: executable specifications (one per significant behavior).
- `decisions/`: Architecture Decision Records.
- `libraries/`: the LLM-maintained wiki, one page per dependency.
- `sources/`: original and normalized external sources.
- `runbooks/`: operational procedures (local dev, verification,
  release, rollback, incident).
- `tools/`: catalog of durable, reusable tools the project has built;
  one card per tool (interface, invocation, tests), indexed by `index.md`.
- `best-practices/`: project-local synthesis of best practices.
- `product/`: user-facing requirements and flows.
- `architecture/`: diagrams and architecture deep dives.
- `api/`: public/internal API references.
- `data/`: data contracts and lineage.
- `evaluations/`: evaluation plans and rubrics for AI behavior.
- `design/`: implementable interface/interaction design specs
  (`ui-ux-designer`), mapped to spec §3/§9.
- `prompts/`: versioned prompts and prompt contracts.
- `legal/`: the legal scope `agent.legal` reasons within (`legal/index.md`).
- `models.md`: the model map, naming the model each host runs for a
  model class and effort.
- `changelog.md`: meaningful project changes.

## Conventions

- Section numbers in `grill.md` and spec files are stable because agents
  and tooling index into them; new content takes a new number.
- ADRs are numbered monotonically: `adr-NNNN-short-slug.md`; a replaced
  decision gets a new ADR that supersedes it (`decisions/README.md`).
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
  `tools/index.md`); the `toolcraft` doctrine runs inside that close-out
- Architect → `decisions/` (ADRs)
- Product → `product/`
- Ui-ux-designer → `design/`
- Tester → `evaluations/`, `runbooks/verification.md`
- Reliability → `runbooks/`
- Security → `decisions/` (threat models), `runbooks/incident-response.md`

After adding a leaf, connect it from the owning node with an
`artifacts:` edge (or `libraries:` for a dependency wiki page).
