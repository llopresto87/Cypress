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

## The four kinds of row

Three of them are derived from somewhere other than this file — two from the
SEED and one from the plant's own graph — so a row cannot go missing by being
left out, and a graft to a newer seed adds rows the plant does not yet answer,
which is exactly how "grafted is not grown" becomes visible:

- **collections** — one row per knowledge collection the installer creates
  (every directory and leaf of the seed's `templates/docs/**`, each runbook
  counted separately);
- **agents** — one row per roster agent that declares `plant_knowledge:`, the
  collections it must be able to read before it can do its job on this project
  at all. This is the row that answers "does `ui-ux-designer` have any design
  material here, does `legal` have any corpus, does `implementer` have library
  pages for the stack it is about to write against";
- **experts** — one row per project-specific expert the plant's own graph
  carries: every agent under `docs/graph/agents/` that is not `origin: seed`,
  plus any an inventory row names. Growth is supposed to end with the experts
  this project needs and the base roster does not have — the rarer half of the
  evidence ledger's §9, the signal a node could not answer — and this row is
  what makes that checkable,
  including the part that used to fail silently: an expert authored into the
  graph and never projected into the harness is on disk and unspawnable,
  because the host reads its roster from the projection directory when a
  session starts;
- **inventory** — one row per item the scouts found, carrying its own planned
  artifacts, its own grounding obligation, and — where it is a dominant domain
  or a core part of the stack — its own staffing decision.

## Status vocabulary

Exactly one of, on every collection, agent, and expert row:

- **COVERED** — authored to the depth the evidence supports. Cite the strongest
  `evidence` paths; they must resolve in the plant.
- **ABSENT** — the source genuinely has no such evidence. Give the `reason` and
  the `searched` paths that establish it. A real absence is a fact; an
  unestablished one is a gap wearing a fact's clothes. For an agent or
  expert row, `searched` names where the material would be and was not; a
  filled leaf of this plant's graph listed there is a redirect, not an
  absence (`CONTRADICTED`) — re-home the material into the collection the
  agent reads, or cite the source paths instead.
- **UNKNOWN** — a named `blocker` (unreachable source, a two-round
  non-converging `recover` finding, an evidence gap the scouts could not close)
  prevents coverage. The only legitimate way a row stays uncovered, and it
  ships reported, never silent — named in the plant's `changelog.md` entry
  for the pass (the row, what it waits on, and who) and put to the owner as
  a numbered decision (`deliver.numbered-decisions`), the same ask the
  plant facts use. The audit reads that entry and reports an `UNKNOWN` it
  never names as `SILENT`, which fails the gate.

`ran out of context`, `seemed enough`, `templates are present`, and `common
cases done` are not statuses — they are the failure the contract forbids.

## The staffing decision

An inventory item of kind `domain`, and any item marked `significance: core`,
carries an `expert` object. It is the ledger §9 signal recorded where it
survives the run — and the question it answers is no longer "does this surface
deserve an agent?".

**The node is owed; an agent needs a trigger.** Every core or significant stack
element already owes an `expertise.*` node (the table below derives it, and
`--plan` writes the path), and that node is the default answer to "who knows
this here": the router composes it into any worker whose task names it, at no
cost to the roster. So an **agent** is warranted only for what a node cannot
be — work that needs different `tools`, a different `model` class, an
adversarial `stance`, or context `isolation`. `warranted: true` therefore names
which of those four it `needs`, alongside a `name` and a `why`:

```json
"expert": {"warranted": true, "name": "claims-adjudication-expert",
           "needs": "isolation",
           "why": "every rule change touches parser, engine, and audit trail;
                   the adjudication pass has to reason on the rule text alone,
                   uncontaminated by the caller's context"}
```

```json
"expert": {"warranted": false,
           "why": "expertise.dotnet already carries when this is in play and
                   what not to do without it; no work here wants other tools,
                   another model class, an adversarial stance, or its own
                   context"}
```

A `why` that only says the surface matters is not a reason to spawn — say what
the expertise node could not do. `warranted: true` missing any of `name`,
`why`, or a `needs` drawn from those four is not a decision, it is
`UNSTAFFED`; so is a `name` that resolves to no agent node in the plant, which
means the surface was staffed on paper only. `warranted: false` is complete
with its `why`. What an item may not do is leave the question unasked, because
a decision nobody recorded is indistinguishable from a §9 nobody read, and that
is the state plants kept arriving in. An expert the plant's graph carries that
the record has no row for is `MISSING` — re-run `--plan`, which derives the row
from the plant's own graph.

An expert the plant carries owes four things beyond existing: `origin: project`
in its frontmatter, so a graft can tell it from the seed machinery it replaces;
a `plant_knowledge:` list — the collections or expertise nodes it draws on — so
the agent authored *for* this project's surface is not the only one exempt from
the check that asks whether it has anything to read; a `motivated_by` citation
in its row, resolving to the source that earned it; and a projection at every
path the plant's `.cypress/seed.json` stamp records under `agent_projections`,
byte-identical to its graph home wherever that entry says `"verbatim": true`
(where it says false the projection is generated at install time, so it is
checked for presence, not for sameness). The installer writes those paths
because the installer is what creates them; nothing else keeps a copy of that
mapping.

## Inventory kinds and what each owes the graph

`--plan` fills these defaults; the orchestrator extends them from evidence but
may not silently drop one. `grounding.required` means a `research-scout` must
retrieve the upstream documentation this run and normalize it under
`docs/graph/sources/` — the page is written from what was retrieved, never from
model memory. Each normalized source keeps its raw snapshot under
`sources/raw/`, or names in its `raw:` line why none was kept; the `sources/`
collection row is `UNJUSTIFIED` otherwise.

| kind | planned artifacts | expertise node | grounded |
|---|---|---|---|
| `language`, `runtime`, `framework` | `libraries/<slug>.md`, `best-practices/<slug>.md` | yes (its `libraries:` names `<slug>`) | yes |
| `dependency` (core / significant) | `libraries/<slug>.md` | yes (its `libraries:` names `<slug>`) | yes |
| `dependency` (incidental) | a row of `libraries/index.md` naming it (the line is the artifact; the audit looks for the row, not the file) | no | no |
| `infrastructure` | `architecture/<slug>.md`, `best-practices/<slug>.md` | yes | yes |
| `datastore` | `data/<slug>.md`, `best-practices/<slug>.md` | yes | yes |
| `external-service` | `architecture/<slug>.md` | no | yes |
| `ai-provider` | `prompts/<slug>.md`, `evaluations/<slug>.md` | no | yes |
| `design-surface` | `design/<slug>.md` | no | yes |
| `regulatory-exposure` | `legal/<slug>.md` | no | yes |
| `domain` | whatever the evidence names | no | no |

An expertise node is `nodes/expertise.<slug>.md`. When the inventory carries
one slug at two majors, the node composes one child per major
(`nodes/expertise.<slug>-<major>.md`), and `--plan` says so.

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
      "expert": {"warranted": false, "why": "expertise.dotnet covers it; nothing here needs its own tools, model, stance, or context"},
      "evidence": ["src/Api/Api.csproj:4"],
      "expect": [
        {"path": "libraries/dotnet.md", "why": "core runtime"},
        {"path": "best-practices/dotnet.md", "why": "the standards it is held to"},
        {"path": "nodes/expertise.dotnet.md", "why": "when it is in play, and what it composes"}
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
  ],
  "experts": [
    {"name": "claims-adjudication-expert", "status": "COVERED",
     "home": "docs/graph/agents/claims-adjudication-expert.md",
     "reads": ["architecture/", "best-practices/"],
     "motivated_by": ["src/Claims/Adjudicator.cs:88"],
     "evidence": [], "reason": "", "searched": [], "blocker": ""}
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
