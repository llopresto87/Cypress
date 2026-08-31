---
name: adopt-existing
description: Source-first growth of an existing single- or multi-repository project into CYPRESS's unified docs/graph knowledge system. Use from initialize when code already exists, or for a graph refresh after material code changes. Scout executable evidence, model subsystem nodes, build project-specific architecture/product/API/data/dependency/prompt/operations leaves, connect them for progressive discovery, and validate navigation. Never trust centralized prose without source corroboration, invent specs or ADRs, modify application files, run application builds, or push Git.
id: skill.adopt-existing
tier: 2
kind: skill
origin: seed
title: adopt-existing — grow an existing codebase into the docs/graph knowledge plant, source-first
owns:
  - adopt-existing.method
  - adopt-existing.refresh
  - adopt-existing.validation
requires:
  - protocol.grow
peers:
  - protocol.initialize
  - skill.knowledge-graph
  - skill.from-scratch-bootstrap
load_when:
  - "adopt an existing codebase into the graph"
  - "initialize cypress on a project that already has code"
  - "refresh the knowledge graph after material code changes"
  - "onboard a multi-repo or monorepo project"
  - "build docs/graph for existing source"
artifacts:
  - templates/prompts/graph-session-bootstrap.md
  - templates/prompts/handback-payload.md
est_tokens: 1600
---

# Adopt an existing project

Turn a generic installed seed into a project-specific knowledge plant.
Follow `docs/graph/protocols/initialize.md`; this skill supplies the existing-project
discovery and authoring discipline.

## Invariants

- `docs/graph/` is the only maintained knowledge root. The router, nodes,
  LLM wiki, provenance, plans, runbooks, contracts, and deep dives are
  layers of one graph, not separate documentation systems.
- Executable source outranks prose. Manifests, entry points, routes,
  schemas, migrations, config, deployment, tests, CI, prompts, and evals
  are primary evidence. Existing docs are corroborating evidence only.
- Make additive knowledge changes. Preserve application code and unrelated
  existing files. Never delete or relocate competing AI configurations.
- Do not run builds or application test suites during adoption. Extract
  their exact commands and label them `discovered, not executed`. An
  inherited suite is untrusted until it has been proven by mutation (see
  `docs/graph/protocols/test-first.md` — prove RED by mutation); record it as discovered,
  never as passing.
- Do not fetch, pull, switch, commit, or push. Record repository revision
  as provenance; Git operations need a separate explicit request.
- Observed behavior is not a normative spec. Observed choices are not ADRs
  with invented rationale. Unknown means unknown.

## Scout pass

Establish the governed boundary first: one repo, workspace/monorepo, or an
umbrella of sibling repos. For each repository record path, branch, HEAD,
worktree state, role, manifests, and stack. Boundaries follow capabilities,
not repository count.

Inventory cheaply, excluding generated/vendor/cache/build output. Then
open the smallest authoritative files needed to trace:

1. bootstrap and runtime entry points;
2. module/service/package boundaries and imports;
3. inbound APIs, messages, scheduled work, and outbound integrations;
4. entities, schemas, migrations, storage, and data movement;
5. config/secrets interfaces, deployment, and observability;
6. tests, CI, scripts, prompts, evaluations, and operational commands;
7. direct dependencies and evidence of their actual usage.

Return facts with exact paths and symbols. When prose makes a claim, find
source corroboration or record it as untrusted/unverified. Do not let a
central docs repository become the authority by repetition.

Every delegated worker's brief embeds the canonical block from
`docs/graph/templates/prompts/graph-session-bootstrap.md` — this file does not
restate that discipline.
When a codebase's identifiers and domain vocabulary are in a non-English
(or otherwise non-default) natural language, record that explicitly as a
graph fact during adoption. Downstream agents must grep and reason in the
codebase's actual language rather than an assumed one; an unrecorded
language mismatch silently defeats every later search.

## Librarian pass

Normalize the evidence into single fact owners:

- configure `ROOT_ID` and `KINDS` in `docs/graph/graph-lint.py`;
- author a root node and capability/subsystem nodes;
- factor shared stack, platform, data, domain, and cross-cutting facts into
  their own nodes only where this reduces duplication;
- give nodes concrete `load_when` triggers and source paths;
- keep `requires` minimal and acyclic; use `peers` for boundaries;
- link detailed leaves using `artifacts:` and dependency wiki pages using
  `libraries:`.

Then enrich the leaf collections under `docs/graph/`:

| Collection | Source-grounded content |
|---|---|
| `product/` | actors, capabilities, flows, observed constraints |
| `architecture/` | context, components, runtime flows, integrations, sharp edges |
| `api/` | observed HTTP/RPC/event/job contracts with code locations |
| `data/` | ownership, schemas, persistence, migrations, lineage |
| `libraries/` | all direct deps indexed; critical deps richly wikified |
| `sources/` | provenance for external information actually used |
| `prompts/` | discovered prompt contracts, versions, and call sites |
| `evaluations/` | discovered datasets, rubrics, gates, and failure modes |
| `runbooks/` | exact operational and verification commands, with status |
| `plans/` | evidence gaps, drift/backfill work, next useful increment |
| `best-practices/` | conventions demonstrated by this project |

Keep `specs/` and `decisions/` indexes, but leave them empty unless genuine
intent records already exist and can be preserved with provenance. Put
implementation observations in nodes or architecture leaves.

When the sweep confirms zero test or gate infrastructure, the librarian
pass MUST still emit explicit `absent (YYYY-MM-DD) — <reason>` rows for the
standard gates in the verification runbook, rather than leaving it blank. A
blank runbook is indistinguishable from one nobody checked; recording each
gate as deliberately absent turns an unknown into a stated finding.

When a legacy or parallel documentation source predates and conflicts with
the evidence-derived graph, excluding it as evidence is not enough — do not
merely stop reading it. Silence reads to a later agent as
absence-of-a-decision, and the artifact gets rediscovered and re-trusted.
Give the exclusion a real, routable node that states (a) the source is
excluded as evidence, (b) what supersedes it, and (c) that this is a
trust/evidence decision, NOT authorization to modify or delete the artifact
(see Invariants: never delete or relocate competing configurations). The
Handoff's excluded-docs report then points at this node rather than standing
in for it.

## Dependency wiki depth

Index every direct dependency from manifests. Create a detailed library
page during initialization when the dependency is architecturally
significant, security/operations critical, unusual, or used across several
subsystems. Each page answers how this project uses it, where configuration
lives, relevant constraints, sharp edges, and verification status.

Installed versions come from manifests/locks. Upstream lifecycle,
compatibility, or current guidance requires a primary upstream source;
otherwise mark it pending rather than guessing. Record consulted sources
in `docs/graph/sources/`.

## Refreshing an existing graph

Treat graph prose as a read model to verify against current source:

1. compare repository revisions with the graph changelog/provenance;
2. scout changed areas and their dependency/data/API blast radius;
3. update the existing fact owner instead of creating a duplicate;
4. preserve valid hand-authored context;
5. remove or supersede stale seed-owned claims only with cited contrary
   evidence;
6. record conflicts and unanswered questions in the plan.

Never claim a full refresh when part of the governed source was unavailable.

## Validation

Run knowledge checks only:

```sh
python3 docs/graph/graph-lint.py
python3 docs/graph/graph-lint.py --plan "change a representative capability"
```

Verify all graph links resolve; every Tier-3 leaf is reachable from an
owning node; no duplicate fact homes exist; representative task routes are
small and relevant; commands say whether they were executed; where no test
or gate infrastructure was found, the verification runbook carries explicit
`absent (YYYY-MM-DD) — <reason>` rows for the standard gates rather than a
blank template; and no template placeholders, fabricated success, inferred
specs, or invented rationale remain.

Use known-answer navigation questions from several capabilities plus an
adversarial false-premise question. A wrong or bulk-read answer is a graph
defect: improve ownership, routing, or leaf content and rerun — **at most
two fix-and-rerun rounds per defect** (`docs/graph/protocols/recover.md`); a defect
that survives them is recorded as an honest unknown in the handoff and
handed to the user, never looped on a third time.

## Handoff (the stopping condition)

Adoption is DONE when validation passes within its bounded rounds and the
open defects are recorded — not when every file has been read; completeness
is measured by reliable progressive discovery, not file count. End with
the payload from `docs/graph/templates/prompts/handback-payload.md`, and report:
repository revisions, evidence inspected, graph artifacts created or
refreshed, validation outcomes, docs deliberately excluded as untrusted
(named by their exclusion node, not merely mentioned in passing),
remaining unknowns, and one highest-leverage next action with its tier.
