<!--
Template: prompts/growth-coverage-record.md
THE CANONICAL SCHEMA of the growth coverage record — the artifact that
makes protocols/grow.md's completeness contract
(grow.completeness-contract) mechanical instead of a matter of judgment,
and that lets any later session ask a plant what growth actually covered.

It supersedes the prose "growth completeness ledger" (through 7.2.1),
which was a table a model filled in about its own work, written to
gitignored scratch and discarded when the run ended. A plant therefore
kept no durable answer to "what did growth cover, and what did it
deliberately leave alone?" — and the collections nobody ever looked at
were indistinguishable from the ones a project genuinely has no evidence
for. This record is the same promise, written where it survives and in a
shape a linter reads.

WHO FILLS IT — the ORCHESTRATION chat, not a spawned worker.

WHERE IT LIVES — tracked, beside the plant's seed stamp:

    .cypress/coverage.json

Not `.cypress/growth/`, which is the run's transient scratch and stays
gitignored; not `docs/graph/`, which is the plant's own knowledge. The
coverage record is a fact about the SEED's work on the plant, so it
lives with the seed's other plant-side state — and it is committed,
because its whole purpose is to outlive the run that wrote it.

Discipline: protocols/grow.md (grow.completeness-contract), the
tool that reads it (tools/growth-audit.py), protocols/graft.md
(Phase 5 and the Phase 7 coverage gate).
-->

# Growth coverage record — the schema of `.cypress/coverage.json`

## The loop this record serves

```text
inventory  ->  plan  ->  growth/graft  ->  lint --+
                                                  |
    ^                                             |
    +---------- repeat while findings remain -----+
```

**Inventory** is what the growth scouts found the project to actually be made
of. **Plan** turns each inventory item into the artifacts growth owes it, and
records whether the item needs upstream documentation retrieved from the open
web. **Growth** authors them. **Lint** — `tools/growth-audit.py` — checks each
planned artifact appeared and is not a scaffold. A finding is not a report the
run ends on: it names a row still owed, so the cycle turns again. The gate is
green or growth is not done.

## The three kinds of row

Two of them are derived from the SEED, never from this file, so a row cannot go
missing by being left out — and a graft to a newer seed adds rows the plant
does not yet answer, which is exactly how "grafted is not grown" becomes
visible:

- **collections** — one row per knowledge collection the installer creates
  (every directory and leaf of the seed's `templates/docs/**`, each runbook
  counted separately);
- **agents** — one row per roster agent that declares `plant_knowledge:`, the
  collections it must be able to read before it can do its job on this project
  at all. This is the row that answers "does `ui-ux-designer` have any design
  material here, does `legal` have any corpus, does `implementer` have library
  pages for the stack it is about to write against";
- **inventory** — one row per item the scouts found, carrying its own planned
  artifacts and its own grounding obligation.

## Status vocabulary

Exactly one of, on every collection and agent row:

- **COVERED** — authored to the depth the evidence supports. Cite the strongest
  `evidence` paths; they must resolve in the plant.
- **ABSENT** — the source genuinely has no such evidence. Give the `reason` and
  the `searched` paths that establish it. A real absence is a fact; an
  unestablished one is a gap wearing a fact's clothes.
- **UNKNOWN** — a named `blocker` (unreachable source, a two-round
  non-converging `recover` finding, an evidence gap the scouts could not close)
  prevents coverage. The only legitimate way a row stays uncovered, and it
  ships reported, never silent.

`ran out of context`, `seemed enough`, `templates are present`, and `common
cases done` are not statuses — they are the failure the contract forbids.

## Inventory kinds and what each owes the graph

`--plan` fills these defaults; the orchestrator extends them from evidence but
may not silently drop one. `grounding.required` means a `research-scout` must
retrieve the upstream documentation this run and normalize it under
`docs/graph/sources/` — the page is written from what was retrieved, never from
model memory.

| kind | planned artifacts | grounded |
|---|---|---|
| `language`, `runtime`, `framework` | `libraries/<slug>.md`, `best-practices/<slug>.md` | yes |
| `dependency` (core / significant) | `libraries/<slug>.md` | yes |
| `dependency` (incidental) | a line in `libraries/index.md` | no |
| `infrastructure` | `architecture/<slug>.md`, `best-practices/<slug>.md` | yes |
| `datastore` | `data/<slug>.md`, `best-practices/<slug>.md` | yes |
| `external-service` | `architecture/<slug>.md` | yes |
| `ai-provider` | `prompts/<slug>.md`, `evaluations/<slug>.md` | yes |
| `design-surface` | `design/<slug>.md` | yes |
| `regulatory-exposure` | `legal/<slug>.md` | yes |
| `domain` | whatever the evidence names | no |

A `best-practices/` page is **normative**: the external standard, cited from
what was retrieved, and where this project observably stands against it —
including the things the standard says not to do that this project does. "Here
is what the project happens to do" alone is description and belongs in
`architecture/`.

## Shape

```json
{
  "schema": "cypress.coverage/1",
  "seed_version": "<the seed this was planned against>",
  "run": "grow | graft | adopt",
  "inventory": [
    {
      "kind": "runtime",
      "name": "dotnet",
      "slug": "dotnet",
      "version": "9.0",
      "significance": "core | significant | incidental",
      "status": "COVERED",
      "evidence": ["src/Api/Api.csproj:4"],
      "expect": [
        {"path": "libraries/dotnet.md", "why": "core runtime"},
        {"path": "best-practices/dotnet.md", "why": "the standards it is held to"}
      ],
      "grounding": {
        "required": true,
        "sources": ["docs/graph/sources/normalized/dotnet-9-release-notes.md"]
      }
    }
  ],
  "collections": [
    {"name": "design/", "status": "COVERED", "leaves": 3,
     "evidence": ["docs/graph/design/checkout.md"],
     "reason": "", "searched": [], "blocker": ""}
  ],
  "agents": [
    {"name": "ui-ux-designer", "reads": ["design/", "best-practices/"],
     "status": "COVERED", "artifacts": ["docs/graph/design/checkout.md"],
     "reason": "", "searched": [], "blocker": ""}
  ]
}
```

## The gate

```sh
python3 <seed>/tools/growth-audit.py <plant> <seed> --plan   # create / refresh
python3 <seed>/tools/growth-audit.py <plant> <seed>          # the gate
```

Growth is done ONLY when that gate exits 0, Phase 6 independent validation
passes, and the maturity test at the foot of `docs/graph/protocols/grow.md` is
met — against the graph, never the file tree.
