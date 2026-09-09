<!--
Template: knowledge-graph/_schema.md
Lives at: docs/graph/_schema.md
Used: as the node contract the graph-lint.py linter enforces.
On install/adoption, copy this file and graph-lint.py into docs/graph/,
then replace {{PLACEHOLDERS}} with the project's own kinds and root id.
This file is documentation for humans and agents; the machine-checked
rules live in graph-lint.py.
-->

# The knowledge graph — node contract

This file defines the shape of every node under `docs/graph/nodes/`.
It is the contract `graph-lint.py` enforces. Read it once; after that,
copy an existing node.

## Why a graph and not a folder of docs

A large or multi-repo codebase does not fit in a context window, and a
flat `docs/` tree gives an agent no way to decide what *not* to read.
The graph makes context loading a **traversal with a stopping rule**:

- Nodes are the unit of loading. One node ≈ one subject.
- `requires:` edges are the closure an agent **must** load to work on
  this node correctly. Follow them transitively.
- `peers:` edges are subjects an agent **must not** load unless the
  task explicitly crosses into them. They exist so you know what you
  are choosing not to read.
- `composes:` edges are a menu rather than a closure: an expertise node
  lists its specialisations, and the router descends into only those the
  task names specifically. They exist so depth is available without
  every task paying for all of it.
- Tiers bound the depth. Tier 3 is the collection of project-knowledge
  leaves below `docs/graph/`; a leaf is opened only when a loaded node
  names it and the task needs it.

The result: an agent working on one subsystem loads a few nodes, not
the whole tree, and can say precisely what it did not read and why.

## Tiers

These are the graph **load-tiers** (what loads, and when) — the axis the node
`tier:` field records. They are distinct from the **task tier** (T0–T3, the
risk classification in kernel §0) and the **model class** (sonnet/opus): three
axes that share the word loosely, only the risk axis written `T0–T3`.

| Tier | What | Loaded |
|---|---|---|
| 0 | `AGENTS.md` / `CLAUDE.md` | Always, by the host tool — a bootstrap only: identity, first move, tiers, rule anchors, boundaries |
| 1 | `docs/graph/index.md` | Every task, first |
| 2 | `docs/graph/nodes/*.md` (project) and `docs/graph/{protocols,skills,agents,method}/*.md` (machinery) | By traversal from the router |
| 3 | `docs/graph/{libraries,sources,specs,decisions,plans,runbooks,product,architecture,api,data,evaluations,prompts,best-practices,tools,templates}/**` | Only when a Tier-2 node names it AND the task needs it |

**Machinery nodes.** The seed's method surface — protocols (how work
flows), skills (how a technique is executed), agents (who does what),
and method nodes (tiers, delegation, engineering posture) — lives
inside the graph as Tier-2 nodes of kind `protocol`/`skill`/`agent`/
`method`, each in its kind's directory. They carry `origin: seed`
(graft's ownership marker), route through this same schema, and load
progressively exactly like project nodes: nothing about *how to work*
is always-loaded except the kernel bootstrap. Two project-fact checks
do not apply to them (version-pin leakage; the ~150-line body ceiling),
and their filenames keep natural names — the id's `<name>` part must
equal the filename stem with any `NN-` ordering prefix stripped.
Templates under `docs/graph/templates/**` are Tier-3 artifacts (blank
forms carry no routable knowledge); machinery nodes point at them via
`artifacts:`.

## Frontmatter

Every node begins with YAML frontmatter (a small subset: `key: scalar`
or `key:` followed by two-space-indented `  - item` lines — no nested
maps, no inline `[a, b]` lists).

```yaml
---
id: {{kind}}.{{name}}          # unique, dotted, lowercase
tier: 2
kind: {{kind}}                 # one of the project's node kinds (below)
title: {{name}} — one-line description
repo: {{repo-or-path}}         # optional; omit for non-code subjects
owns:                          # facts this node is the SOLE home of
  - {{name}}.responsibility
  - {{name}}.{{another-fact}}
requires:                      # transitive closure; ALWAYS loaded with this node
  - {{kind}}.{{dependency}}
peers:                         # NOT loaded unless the task crosses into them
  - {{kind}}.{{neighbour}}
composes:                      # lazy, downward, expertise nodes only; descended into
  - expertise.{{sub-slug}}     # only for the children the task names specifically
libraries:                     # Tier-3 wiki pages this node depends on (optional)
  - {{library-name}}
artifacts:                     # graph-relative knowledge leaves (optional)
  - architecture/{{subject}}.md
  - api/{{contract}}.md
load_when:                     # natural-language triggers for the router
  - "editing {{repo-or-path}}/**"
  - "{{concept}}, {{synonym}}, {{the phrase a dev would type}}"
est_tokens: {{honest-estimate}}
status: open                   # lifecycle status (optional on most kinds; see below)
status_date: YYYY-MM-DD
owner: {{agent-or-person}}     # required while open | hotfix | deferred
---
```

### Lifecycle status

Anything that can be *open* carries its status **in frontmatter, never in
prose** — an agent must read a field, not infer a state. One base vocabulary
for every kind:

| value | means | requires |
|---|---|---|
| `open` | live, unresolved | `owner` |
| `deferred` | deliberately parked | `owner`, `reopen_when` |
| `hotfix` | resolved **improperly**; a proper fix is owed — never reads as closed | `owner` |
| `rejected` | considered and declined; the reason is in the body | — |
| `superseded` | replaced | `superseded_by` |
| `closed` | resolved **with evidence** | `status_evidence` (a path#anchor, commit, or gate-run id) |

Kind extensions, only where the base cannot express a real state: ADR adds
`proposed | accepted`; spec adds `draft | active | implemented | back-written`
(back-written = documented existing behaviour, untested); `deviation` adds
`standing` (permanently open by design; requires `ends_when`). `status_date`
is always present. A body `## Status` section may exist only as a pointer to
the frontmatter; a body value that disagrees is a lint failure — two homes
for one fact is how status drift starts. `legal_status` in the legal corpus
is a *domain* fact (in force / repealed), not a lifecycle, and is separate.

`graph-lint.py` checks status on every node it loads; the delivered
`status-register.py` checks Tier-3 leaves (ADRs, specs, risk rows) and is
the query surface (`--open --hotfix --summary`) a session-start hook injects.

### Node kinds

Each project defines its own small set of kinds and sets them in
`graph-lint.py` (`KINDS`). Pick kinds that carve the project at its
joints. A common starting set:

- `root` — the single entry node describing the whole project and its
  map. (Its id is exactly the root id, e.g. `root` or `program`.)
- `subsystem` — a service, package, or module.
- `stack` — a language/framework's shared conventions **in this
  project**: layout, build, house rules, which projects target what.
  Requires the matching `expertise.*` node and never restates its
  applicability.
- `expertise` — **when** a language, runtime, framework, library, or
  platform is in play for a task, what must not be done without it, and
  which sub-expertises apply under which condition. Lives in `nodes/`
  as `expertise.<slug>.md`, the slug unversioned (see `composes`). Owns
  exactly `<slug>.applicability` and `<slug>.composition`; every fact,
  pin, and standard stays in `libraries/` and `best-practices/`,
  reached by `libraries:`/`artifacts:` — an expertise node with no such
  depth edge routes to nothing and fails lint. Where a plant runs two
  majors of one stack at once, the unversioned node composes one child
  per major (`expertise.dotnet-8`), the only place a version enters a
  slug; the retired child is `superseded`.
- `platform` — infra: gateway, config, discovery, messaging, deploy,
  observability.
- `data` — the data model and where it lives.
- `crosscut` — concerns spanning subsystems: auth, secrets, privacy,
  testing.
- `domain` — the problem-domain vocabulary and workflows.

- `deviation` — a **deliberate, standing departure from a known standard**,
  with the reason, its scope, and the condition that ends it. Lives in
  `nodes/` as `deviation.<slug>.md` with `status: standing`, `departs_from`
  (the fact key or standard it departs from), `reason`, `scope`, `ends_when`,
  `recorded_in` (the ADR that holds the history). The ADR is the record;
  the deviation node is the standing truth the router surfaces exactly when
  the topic comes up, so a lapse is never mistaken for a decision or a
  decision re-litigated as a lapse.

Four kinds are reserved for the seed's machinery and always present:
`protocol`, `skill`, `agent`, `method` (see "Machinery nodes" above).

An `id`'s prefix must match its `kind` (`subsystem.orders`,
`stack.python`), except the single root node whose id *is* the root id.
Projects that want a terser namespace may map a kind to a different
prefix via the `KIND_PREFIX` table in `graph-lint.py`'s PROJECT CONFIG
block (e.g. `{"subsystem": "sub"}` lets `sub.orders` carry
`kind: subsystem`); unmapped kinds keep the identity rule. The graft
engine preserves this config across seed updates.

### The `plant:` block (on `index.md`)

The router's own frontmatter carries the facts **only the owner can assert**
and that agents otherwise re-ask or guess:

```yaml
plant:
  environment_class: ephemeral-test | staging | real-production | mixed
  commit_attribution: none | <trailer text>
  deliverable_language: <bcp47>
  comment_language: <bcp47>
```

Asked once, in grow Phase 1 or adopt-existing. `mixed` requires a
per-deployment declaration in the deployment node. Rules about synthetic
data, disposable credentials, rollback readiness, and build-on-host key off
`environment_class` instead of being adjudicated case by case. The linter
**fails** a grown plant that lacks the block and **warns** an adopted one.

## Key semantics

**`owns`** — the dedup mechanism, and the most important key. Each
entry is a fact-key this node is the single source of truth for. A
fact-key appears in exactly one node's `owns` list, project-wide. If
two nodes both want a fact, extract it to a shared node and have both
`require` it.

**`requires`** — hard dependency; you cannot be correct on this node
without them. Keep minimal — every edge is context every future agent
pays for. Must be acyclic on its own (see `composes`).

**`peers`** — soft adjacency; the boundary you are not crossing. The
router prints these as "not loaded" so the choice is visible.

**`composes`** — lazy, downward, and task-conditioned; expertise nodes
only, toward expertise nodes only. Where `requires` is a closure the
router always takes, `composes` is a menu it reads: a composed child
loads only when the task names, exactly, a term in the child's own
vocabulary — its `load_when` tokens and its whole slug, minus the
parent's. Family words on the parent therefore never descend a child;
a child's triggers must be its own. `composes` is acyclic on its own.
Its union with `requires` is deliberately not: `parent composes child`
and `child requires parent` is the intended shape (the eager edge
points up, the lazy one down), and a child that `requires` an expertise
node must appear in that node's `composes` — lint names the line to
add. The router prints un-composed children as "not loaded" with the
reason, so the choice is visible.

**`artifacts`** — progressive-discovery edges from a node to detailed
knowledge leaves. Paths are relative to `docs/graph/`, must remain
inside it, and must resolve. `libraries` is the specialized wiki edge;
all other leaf kinds use `artifacts`.

**`load_when`** — what the router matches a task description against.
On `kind: agent` nodes, `routing_triggers` (the same key the harness
roster uses) substitutes for `load_when` — the linter accepts either;
all shipped agent nodes use `routing_triggers`.
Write the phrases a developer would actually type, including globs.

**`est_tokens`** — honest estimate of the node's own body. The router
sums these to report context cost before work starts.

## Body

Answer, in this order, and nothing else: **what this is** (2–3
sentences) · **what you must know** (the owned facts, terse) · **sharp
edges** (what will bite, dated) · **where the code is** (concrete
paths) · **neighbours** (why each peer exists, when to cross). Under
~150 lines (the linter rejects past 170); a longer node is two nodes.

An `expertise` node answers a routing question instead, so its order is
**what this is in play for** · **what you must not do without it** ·
**composition** (one line per composed child, naming the condition it
applies under) · **version in play** (a pointer to
`libraries/<slug>.md`, never a version) · **depth** (which leaf serves
which purpose). The same ceiling applies, and is generous: a node that
needs more room is restating a leaf.

## The rules the linter enforces

1. Frontmatter parses and has every required key.
2. `id` is unique and matches the filename (`<id>.md`).
3. `id` prefix matches `kind` (root node excepted).
4. Every fact-key in `owns` is unique across all nodes.
5. Every id in `requires` and `peers` resolves to a real node
   (`composes` has its own rule, 15).
6. `requires` is acyclic.
7. Every node is reachable from the root by edges, or is listed in
   `index.md`.
8. Every id in `libraries` has a page in `docs/graph/libraries/`.
9. Every path in `artifacts` resolves beneath `docs/graph/`.
10. Version pins do not appear in a node body unless it owns a
   `*.version`/`*.versions` fact-key. Versions belong in
   `docs/graph/libraries/`. Fenced and inline code are exempt —
   quoting a real config line is not restating a fact.
11. `est_tokens` is within 2× of the measured body size; body under the
    line ceiling.
12. `status`, where present, is a vocabulary value for the node's kind and
    carries its required companions (`owner`, `reopen_when`, `superseded_by`,
    `status_evidence`, `ends_when`); a body `## Status` value never disagrees.
13. A `deviation` node has `status: standing`, `departs_from`, `reason`,
    `scope`, `ends_when`, `recorded_in`.
14. `index.md` carries a complete `plant:` block — failure on a grown plant,
    warning on an adopted one.
15. Every id in `composes` resolves, and both ends are `kind: expertise`.
16. `composes` is acyclic (its union with `requires` is not checked; see
    `composes`).
17. An expertise node that `requires` an expertise node is listed in that
    node's `composes`.
18. An expertise node has at least one `libraries` or `artifacts` edge.
19. An expertise id ending in `-<digits>` is composed by the id without the
    suffix.

```sh
python3 docs/graph/graph-lint.py            # lint
python3 docs/graph/graph-lint.py --graph    # print the edges: `→` requires, `~>` composes
python3 docs/graph/graph-lint.py --plan "<task>"   # dry-run the router
```

## Anti-patterns

- **A node that restates a version** — link to the library page.
- **An expertise node that names the version instead of pointing at
  it** — the pin has one home; the node says where, never what.
- **A node that `requires` everything** — a bulk read in disguise.
- **An expertise node that `composes` everything** — the same bulk read
  wearing a menu. If every child descends on every task, the children
  are carrying the family's words instead of their own.
- **A subsystem node that explains the language/framework** — that is a
  `stack.*` node.
- **An expertise node that restates its own leaf** — it owns when the
  depth is in play, not what the depth says.
- **A node with no `owns`** — a link farm; delete it.
- **Growing a node instead of splitting it** at the line ceiling.
- **Filling an unknown with a guess** — write "not recorded".
- **A status stated in prose** — a state nobody can query is a state
  everybody re-infers; put it in frontmatter.
- **`closed` without evidence** — that is `hotfix` or `deferred` wearing a
  green badge.
