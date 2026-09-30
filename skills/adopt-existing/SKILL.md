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
  - protocol.from-scratch
load_when:
  - "adopt an existing codebase into the graph"
  - "initialize cypress on a project that already has code"
  - "refresh the knowledge graph after material code changes"
  - "onboard a multi-repo or monorepo project"
  - "build docs/graph for existing source"
artifacts:
  - templates/prompts/graph-session-bootstrap.md
  - templates/prompts/handback-payload.md
prevents: An adoption with no way back — a graph authored once from a snapshot of the code, with no refresh path when the source moves under it, so it decays into a confident description of a repository that no longer exists.
est_tokens: 1780
---

# Adopt an existing project

Turn a generic installed seed into a project-specific knowledge plant.
Follow `docs/graph/protocols/initialize.md`; this skill supplies the
existing-project discovery and authoring discipline.

## Invariants

- `docs/graph/` is the only maintained knowledge root. The router,
  nodes, LLM wiki, provenance, plans, runbooks, contracts, and deep
  dives are layers of this one graph (`rule.knowledge`).
- Executable source outranks prose. Manifests, entry points, routes,
  schemas, migrations, config, deployment, tests, CI, prompts, and evals
  are primary evidence. Existing docs are corroborating evidence only.
- Make additive knowledge changes. Preserve application code and
  unrelated existing files. Leave competing AI configurations in place;
  deleting or relocating one is the owner's call.
- Adoption ONLY records build and test commands: extract each exact
  command and label it `discovered, not executed`. An inherited suite
  stays untrusted until proven RED by mutation
  (`docs/graph/protocols/test-first.md`), so record it as discovered.
- Git stays read-only: record the repository revision as provenance;
  fetch, pull, switch, commit, and push each need a separate explicit
  request.
- Record observed behaviour and observed choices as node facts. Specs
  and ADRs record intent, which only an existing record or the owner
  supplies. Unknown means unknown.

## Scout pass

Establish the governed boundary first: one repo, workspace/monorepo, or
an umbrella of sibling repos. For each repository record path, branch,
HEAD, worktree state, role, manifests, stack, and the natural language
of its identifiers and domain vocabulary. A non-English (or otherwise
non-default) language is an explicit graph fact, because downstream
agents grep and reason in it and an unrecorded mismatch silently defeats
every later search. Boundaries follow capabilities, not repository
count.

Inventory cheaply, excluding generated/vendor/cache/build output. Then
open the smallest authoritative files needed to trace:

1. bootstrap and runtime entry points;
2. module/service/package boundaries and imports;
3. inbound APIs, messages, scheduled work, and outbound integrations;
4. entities, schemas, migrations, storage, and data movement;
5. config/secrets interfaces, deployment, and observability;
6. tests, CI, scripts, prompts, evaluations, and operational commands;
7. direct dependencies and evidence of their actual usage.

Return facts with exact paths and symbols. Find source corroboration for
each claim prose makes, or record it as untrusted/unverified; repetition
across central docs adds no corroboration.

Every delegated worker's brief embeds the canonical block from
`docs/graph/templates/prompts/graph-session-bootstrap.md`.

## Librarian pass

Normalize the evidence into single fact owners:

- configure `ROOT_ID` and `KINDS` in `docs/graph/graph-lint.py`;
- author a root node and capability/subsystem nodes;
- factor shared stack, platform, data, domain, and cross-cutting facts
  into their own nodes only where this reduces duplication;
- give nodes concrete `load_when` triggers and source paths;
- keep `requires` minimal and acyclic; use `peers` for boundaries, and
  `composes` where an `expertise.*` node offers sub-expertises the
  router should descend into only when the task names one;
- link detailed leaves using `artifacts:` and dependency wiki pages
  using `libraries:`.

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

Keep `specs/` and `decisions/` indexes, and fill them only from genuine
intent records that already exist and can be preserved with provenance.
Put implementation observations in nodes or architecture leaves.

When the sweep confirms zero test or gate infrastructure, write an
`absent (YYYY-MM-DD) — <reason>` row for each standard gate in the
verification runbook: a blank runbook is indistinguishable from one
nobody checked, and a row for each gate turns an unknown into a stated
finding.

When a legacy or parallel documentation source predates and conflicts
with the evidence-derived graph, give the exclusion a real, routable
node that states (a) the source is excluded as evidence, (b) what
supersedes it, and (c) that this is a trust/evidence decision only: the
artifact itself stays untouched (Invariants). A silent skip reads to a
later agent as no decision, and the artifact gets re-trusted. The
Handoff's excluded-docs report then points at this node rather than
standing in for it.

## Dependency wiki depth

Index every direct dependency from manifests. Create a detailed library
page during initialization when the dependency is architecturally
significant, security/operations critical, unusual, or used across
several subsystems. Each page answers how this project uses it, where
configuration lives, relevant constraints, sharp edges, and verification
status.

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

Report a refresh as partial, naming each unavailable source, whenever
part of the governed source was out of reach.

## Validation

Run knowledge checks only:

```sh
python3 docs/graph/graph-lint.py
python3 docs/graph/graph-lint.py --plan "change a representative capability"
```

Verify all graph links resolve; every Tier-3 leaf is reachable from an
owning node; no duplicate fact homes exist; representative task routes
are small and relevant; commands say whether they were executed; the
verification runbook carries the absent-gate rows where no
infrastructure was found (Librarian pass); and no template placeholders,
fabricated success, inferred specs, or invented rationale remain.

Use known-answer navigation questions from several capabilities plus an
adversarial false-premise question. A wrong or bulk-read answer is a
graph defect: improve ownership, routing, or leaf content and rerun, for
at most two fix-and-rerun rounds per defect; with the authoring pass
they are the three attempts `docs/graph/protocols/recover.md` allows. A
defect that survives them goes to the user as an honest unknown.

## Handoff (the stopping condition)

Adoption is done when validation passes within its bounded rounds and
the open defects are recorded; completeness is measured by reliable
progressive discovery. End with the payload from
`docs/graph/templates/prompts/handback-payload.md`, and report:
repository revisions, evidence inspected, graph artifacts created or
refreshed, validation outcomes, docs deliberately excluded as untrusted
(each named by its exclusion node), remaining unknowns, and one
highest-leverage next action with its tier.
