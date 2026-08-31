---
name: knowledge-graph
description: Build and maintain the project's knowledge graph — a tiered set of nodes under docs/graph/ that lets an agent load only the few facts a task needs instead of the whole codebase. Use when adopting a project, when a fact changes, when a node grows too large, or when a task should have matched a node's triggers and didn't. Enforces one home per fact (dedup), honest per-node budgets, cite-don't-fabricate, and a mechanical linter. The library wiki (docs/graph/libraries/) is a leaf tier of this graph, not a separate system.
id: skill.knowledge-graph
tier: 2
kind: skill
origin: seed
title: knowledge-graph — author and maintain the tiered node graph the router traverses, lint-enforced
owns:
  - knowledge-graph.method
  - knowledge-graph.node-contract
  - knowledge-graph.linter
requires:
peers:
  - skill.context-router
  - skill.library-wiki
  - skill.validate-knowledge
load_when:
  - "author or edit a graph node"
  - "one home per fact violation"
  - "graph-lint fails"
  - "add or sharpen a load_when trigger"
  - "split an oversized node"
  - "build the docs/graph structure"
artifacts:
  - templates/knowledge-graph/_schema.md
  - templates/knowledge-graph/graph-lint.py
  - templates/knowledge-graph/index.md
  - templates/knowledge-graph/node.template.md
est_tokens: 1700
---

# knowledge-graph

The graph at `docs/graph/` is how a project stays legible when it no
longer fits in a context window. Each node is one subject; edges say
what a task must load with it; tiers bound the depth. An agent starts
at the router index and traverses (see `context-router`); this skill
is the discipline of *authoring and maintaining* what it traverses.

Scale is agnostic: a "subsystem" node may describe a package in a
single repo or a whole repo in a multi-repo program. The graph does
not privilege either shape — nodes describe subjects, and how many
repos those subjects span is a property of the project, not of the
method.

## Tiers

| Tier | What | Loaded |
|---|---|---|
| 0 | The kernel (`AGENTS.md` / `CLAUDE.md`) | Always, by the host tool |
| 1 | `docs/graph/index.md` — the router | Every task, first |
| 2 | `docs/graph/nodes/*.md` — one subject each | By traversal from the router |
| 3 | Detailed collections below `docs/graph/` | Only when a Tier-2 node names the leaf and the task needs it |

A Tier-2 node never loads another node's *content* by copying it. It
names the node id and lets the traversal do the work.

## The node contract

Every node begins with frontmatter. The full contract — every key's
semantics (`id`, `owns`, `requires`, `peers`, `artifacts`, `libraries`,
`load_when`, `est_tokens`) and the anti-patterns — lives in
`docs/graph/templates/knowledge-graph/_schema.md`, the file installed beside the
graph itself; copy an existing node rather than authoring frontmatter
from scratch. The key that carries the whole design: `owns` — each
fact-key appears in exactly one node's list, project-wide.

## The rules

### 1. One home per fact

Every fact has exactly one owning node, declared in its `owns` list.
No other file restates it; other files **link**. Duplicated facts rot
asymmetrically — one copy gets updated, the other silently lies, and a
lying doc is worse than a missing one. When two nodes both want a fact,
extract it to a shared node and have both `require` it.

### 2. Version pins live in the library tier

An exact version belongs on its `docs/graph/libraries/<name>.md` page. A
node body may summarize a version only if it owns the corresponding
`*.versions` fact-key; otherwise it links to the page. This keeps a
version from being stated in five places and updated in one.

### 3. Cite; do not fabricate

Every non-obvious claim has a source. **Never invent a URL, a CVE id,
a version, or a fact to fill a section.** Write "not recorded" or "not
audited" instead — an honest gap is usable; a confident fabrication is
a trap. This is the single most important authoring rule, because a
graph exists to be trusted over model memory.

Separate **observed** from **audited**. A fact described because it was
seen in source is not the same as a fact that was audited or certified,
and a page's prose must never let the first read as the second — "the
handler validates the token" (observed in one path) does not mean
"every path validates the token" (a coverage claim nobody checked). Say
which you did. Where a page's scope is partial, add an explicit
**observed absences / what this page is NOT** note, so a reader cannot
mistake the edge of what was surveyed for a guarantee of what holds.

### 4. Bodies stay small

A node body stays under ~150 lines. A node that wants to be longer is
two nodes. `est_tokens` stays within 2× of the real body size — the
router sums these to report context cost before work starts, so a lie
here corrupts every plan.

### 5. Compound, don't restart

Nodes grow with the project. Add a fact when the code gains it; add a
sharp edge when it bites, dated; add a `load_when` trigger when a task
should have matched and didn't. Do not pre-populate theoretical facts.

Compounding extends to being *wrong*: when a recorded fact is later
found false — after testing or a closer survey — do not silently
overwrite it. Add a dated **Correction** note *alongside* the original,
keeping the original (wrong) reasoning and stating the corrected
finding. A future reader needs to see *why* the belief changed, not
just that it did — the discarded reasoning is often what stops the next
agent from re-deriving the same mistake. (This is the single-current-
truth analog of the append-only supersede rule, not a contradiction of
one home per fact: the current fact still has one home; the Correction
records how it got there.)

### 6. One graph, several depths

`libraries/`, `sources/`, `product/`, `architecture/`, `api/`, `data/`,
`prompts/`, `evaluations/`, `plans/`, `runbooks/`, `specs/`, and
`decisions/` are graph leaf collections, not autonomous docs trees. A leaf
without an owning-node edge is orphaned knowledge. Maintained project
knowledge outside `docs/graph/` is an input to corroborate and ingest, not
a second source of truth.

### 7. Never inline secret material

A knowledge page records where a secret lives, never the secret
itself — not a live value, and not a redacted-looking copy either (a
"partially masked" token still leaks its shape, length, and prefix, and
the graph is committed, searchable, and long-lived). Record a
**pointer**: the secret manager path, the env-var name, the vault key —
the fact a reader needs is *where to look*, and that is safe to own.

## Node body shape

Answer, in this order, and nothing else: **what this is** (2–3
sentences) · **what you must know** (the owned facts — terse; bullets,
tables, code) · **sharp edges** (what will bite, dated) · **where the
code is** (concrete paths, not descriptions of paths) · **neighbours**
(why each peer exists and when to cross to it).

## The linter

`docs/graph/` ships a linter (`docs/graph/templates/knowledge-graph/graph-lint.py`,
copied in and parameterized on adoption). It makes the dedup rule real
rather than aspirational. It enforces:

1. Frontmatter parses; required keys present; `id` matches filename and
   kind.
2. Every fact-key in `owns` is unique across all nodes.
3. Every id in `requires`/`peers` resolves; `requires` is acyclic.
4. Every node is reachable from the root or listed in the index.
5. Every `libraries:` id has a page in `docs/graph/libraries/`.
6. Every `artifacts:` path resolves beneath `docs/graph/`.
7. No version pin appears in a node that doesn't own a `*.versions`
   key.
8. `est_tokens` is within 2× of the measured body; bodies under the
   line ceiling.

Run it before committing any graph change:

```sh
python3 docs/graph/graph-lint.py            # lint
python3 docs/graph/graph-lint.py --graph    # print the requires-DAG
python3 docs/graph/graph-lint.py --plan "<task>"   # dry-run the router
```

A graph without a passing linter is a graph that has already started
to lie. Wire it into the verification gates.

An authoring or maintenance pass is DONE when the linter passes, every
new leaf resolves through an owning node's edge, and the facts that
motivated the pass each have exactly one home — not when every possible
node exists. Growth is demand-driven; stop at the passing lint.

## When the graph is wrong

It will be; code moves and the graph lags. When a node contradicts the
code: **the code wins on facts** (fix the node in the same change);
**the node wins on contracts** (a code violation of a recorded contract
is a bug, not a doc update). When a task should have matched a node's
`load_when` and didn't, sharpen the trigger in the same commit.

## Reference files

- `docs/graph/skills/context-router.md` — how the graph is traversed.
- `docs/graph/skills/library-wiki.md` — the Tier-3 library-page discipline.
- `docs/graph/skills/validate-knowledge.md` — proving the graph is usable.
- `docs/graph/templates/knowledge-graph/` — the schema, linter, index, and node
  templates.
