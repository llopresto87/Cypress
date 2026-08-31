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
- Tiers bound the depth. Tier 3 is the collection of project-knowledge
  leaves below `docs/graph/`; a leaf is opened only when a loaded node
  names it and the task needs it.

The result: an agent working on one subsystem loads a few nodes, not
the whole tree, and can say precisely what it did not read.

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
libraries:                     # Tier-3 wiki pages this node depends on (optional)
  - {{library-name}}
artifacts:                     # graph-relative knowledge leaves (optional)
  - architecture/{{subject}}.md
  - api/{{contract}}.md
load_when:                     # natural-language triggers for the router
  - "editing {{repo-or-path}}/**"
  - "{{concept}}, {{synonym}}, {{the phrase a dev would type}}"
est_tokens: {{honest-estimate}}
---
```

### Node kinds

Each project defines its own small set of kinds and sets them in
`graph-lint.py` (`KINDS`). Pick kinds that carve the project at its
joints. A common starting set:

- `root` — the single entry node describing the whole project and its
  map. (Its id is exactly the root id, e.g. `root` or `program`.)
- `subsystem` — a service, package, or module.
- `stack` — a language/framework's shared conventions.
- `platform` — infra: gateway, config, discovery, messaging, deploy,
  observability.
- `data` — the data model and where it lives.
- `crosscut` — concerns spanning subsystems: auth, secrets, privacy,
  testing.
- `domain` — the problem-domain vocabulary and workflows.

Four kinds are reserved for the seed's machinery and always present:
`protocol`, `skill`, `agent`, `method` (see "Machinery nodes" above).

An `id`'s prefix must match its `kind` (`subsystem.orders`,
`stack.python`), except the single root node whose id *is* the root id.

## Key semantics

**`owns`** — the dedup mechanism, and the most important key. Each
entry is a fact-key this node is the single source of truth for. A
fact-key appears in exactly one node's `owns` list, project-wide. If
two nodes both want a fact, extract it to a shared node and have both
`require` it.

**`requires`** — hard dependency; you cannot be correct on this node
without them. Keep minimal — every edge is context every future agent
pays for. Must be acyclic.

**`peers`** — soft adjacency; the boundary you are not crossing. The
router prints these as "not loaded" so the choice is visible.

**`artifacts`** — progressive-discovery edges from a node to detailed
knowledge leaves. Paths are relative to `docs/graph/`, must remain
inside it, and must resolve. `libraries` is the specialized wiki edge;
all other leaf kinds use `artifacts`.

**`load_when`** — what the router matches a task description against.
Write the phrases a developer would actually type, including globs.

**`est_tokens`** — honest estimate of the node's own body. The router
sums these to report context cost before work starts.

## Body

Answer, in this order, and nothing else: **what this is** (2–3
sentences) · **what you must know** (the owned facts, terse) · **sharp
edges** (what will bite, dated) · **where the code is** (concrete
paths) · **neighbours** (why each peer exists, when to cross). Under
~150 lines; a longer node is two nodes.

## The rules the linter enforces

1. Frontmatter parses and has every required key.
2. `id` is unique and matches the filename (`<id>.md`).
3. `id` prefix matches `kind` (root node excepted).
4. Every fact-key in `owns` is unique across all nodes.
5. Every id in `requires`/`peers` resolves to a real node.
6. `requires` is acyclic.
7. Every node is reachable from the root by edges, or is listed in
   `index.md`.
8. Every id in `libraries` has a page in `docs/graph/libraries/`.
9. Every path in `artifacts` resolves beneath `docs/graph/`.
10. Version pins do not appear in a node body unless it owns a
   `*.versions` fact-key. Versions belong in `docs/graph/libraries/`.
11. `est_tokens` is within 2× of the measured body size; body under the
    line ceiling.

```sh
python3 docs/graph/graph-lint.py            # lint
python3 docs/graph/graph-lint.py --graph    # print the requires-DAG
python3 docs/graph/graph-lint.py --plan "<task>"   # dry-run the router
```

## Anti-patterns

- **A node that restates a version** — link to the library page.
- **A node that `requires` everything** — a bulk read in disguise.
- **A subsystem node that explains the language/framework** — that is a
  `stack.*` node.
- **A node with no `owns`** — a link farm; delete it.
- **Growing a node instead of splitting it** at the line ceiling.
- **Filling an unknown with a guess** — write "not recorded".
