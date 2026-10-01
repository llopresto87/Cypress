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
  - knowledge-graph.branch-shape
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
  - "which node owns this best-practices page, expertise node or domain node"
  - "where does a new leaf attach, who gets the artifacts edge"
  - "branch node shape, a menu of leaves"
artifacts:
  - templates/knowledge-graph/_schema.md
  - templates/knowledge-graph/graph-lint.py
  - templates/knowledge-graph/index.md
  - templates/knowledge-graph/node.template.md
  - templates/docs/nodes/_deviation.template.md
  - templates/docs/nodes/_expertise.template.md
prevents: A node set with duplicate homes, dishonest budgets and triggers that never fire — a graph that costs context and returns nothing.
est_tokens: 2925
---

# knowledge-graph

The graph at `docs/graph/` is how a project stays legible when it no
longer fits in a context window. Each node is one subject; edges say
what a task must load with it; tiers bound the depth. An agent starts at
the router index and traverses (see `context-router`); this skill is the
discipline of *authoring and maintaining* what it traverses.

Scale is agnostic: a "subsystem" node may describe a package in a single
repo or a whole repo in a multi-repo program. The graph does not
privilege either shape: nodes describe subjects, and how many repos
those subjects span is a property of the project, not of the method.

## Tiers

| Tier | What | Loaded |
|---|---|---|
| 0 | The kernel (`AGENTS.md` / `CLAUDE.md`) | Always, by the host tool |
| 1 | `docs/graph/index.md` — the fallback map | When the routed plan (`graph-lint.py --plan`) fails, stays empty or looks wrong |
| 2 | `docs/graph/nodes/*.md` — one subject each | By traversal from the router |
| 3 | Detailed collections below `docs/graph/` | Only when a Tier-2 node names the leaf and the task needs it |

A Tier-2 node names another node by id and lets the traversal load its
content.

## The node contract

Every node begins with frontmatter. The full contract (every key's
semantics: `id`, `owns`, `requires`, `peers`, `composes`, `artifacts`,
`libraries`, `load_when`, `est_tokens`) and the anti-patterns live in
`docs/graph/_schema.md`, the file installed beside the graph itself;
copy an existing node rather than authoring frontmatter from scratch.
The key that carries the whole design: `owns`. Each fact-key appears in
exactly one node's list, project-wide.

An `expertise` node ONLY routes. It owns exactly two facts,
`<slug>.applicability` (when this stack element is in play, and what
goes wrong without it) and `<slug>.composition` (which
sub-expertises apply under which condition), and it carries at least one
`libraries:`/`artifacts:` edge to the depth it points at. The API, the
pin, and the standard stay on those leaves; the node names the leaf that
serves each purpose. Its specialisations hang off `composes:`, and a
child that `requires:` its parent must appear in that parent's list: the
linter checks that reciprocity, so a child cannot be added without the
menu learning about it.

**Where a grounded idea attaches.** A `best-practices/` page whose
subject is a discipline, not a language or a file format, is a leaf like
any other, and the only question it raises is which node owns it. Give
it an `expertise.*` node when the subject is a stack element with a pin
home in `docs/graph/libraries/`. Attach it to an existing `domain.*`
node when the graph already owns that concept's vocabulary and
invariants: add the page to that node's `artifacts:`, and add the
departure's own words to that node's `load_when:`, so the page is
reachable on the vocabulary a reader would search with. Author a new
`domain.*` only when neither holds. The evidence is the shelf: every
best-practices page about a stack element is owned by an `expertise.*`
node, and every page about a concept the graph already names is owned by
a `domain.*` node. The page's own shape, its sections and its citation
rule, is the shelf's contract in `docs/graph/best-practices/README.md`,
not this skill's.

## The rules

### 1. One home per fact

Every fact has exactly one owning node, declared in its `owns` list.
Every other file **links** to it. Duplicated facts rot asymmetrically:
one copy gets updated, the other silently lies, and a lying doc is worse
than a missing one. When two nodes both want a fact, extract it to a
shared node and have both `require` it.

Two corollaries. **One name per concept**: a term maps one-to-one onto
the thing it names, a near-miss synonym is a fault rather than an alias,
and the graph uses the name the world already holds. A serialized, wire,
or externally held identifier is a contract, never renamed to match
internal vocabulary; a deliberate mismatch is recorded so nobody "fixes"
it (`skill.holistic-editing` owns the rename mechanics). **Rendered
views are generated, hand-edited files are shaped for their editor**: an
index table or status summary is regenerated from its home
(`status-register.py`), and edits go to that home; the files a human
does maintain (the linter's PROJECT CONFIG, the `plant:` block) stay
comment-bearing, grouped, and stably ordered.

### 2. Version pins live in the library tier

An exact version belongs on its `docs/graph/libraries/<name>.md` page. A
node body may summarize a version only if it owns the corresponding
`*.versions` fact-key; otherwise it links to the page. This keeps a
version from being stated in five places and updated in one.

### 3. Cite, or write "not recorded"

Every non-obvious claim has a source. Where a URL, a CVE id, a version,
or a fact is unknown, write "not recorded" or "not audited"; never
invent one to fill a section. An honest gap is usable, a confident
fabrication is a trap, and a graph exists to be trusted over model
memory.

Separate **observed** from **audited**. A fact described because it was
seen in source is not the same as a fact that was audited or certified,
and a page's prose keeps the two apart: "the handler validates the
token" (observed in one path) is a different claim from "every path
validates the token" (a coverage claim nobody checked). Say which you
did. Where a page's scope is partial, add an explicit **observed
absences / what this page is NOT** note, so a reader cannot mistake the
edge of what was surveyed for a guarantee of what holds. The same split
holds for **traced versus inferred**: a claim not traced to a source,
command output, or dated observation carries an explicit `verify:`
marker naming what to re-check; a procedure page says whether its
commands were run here; unbuilt work is written in the future tense with
its owning increment named, because a present-tense sentence asserts
that the thing exists.

### 4. Bodies stay small

A node body aims at ~150 lines, and the linter rejects a project node
whose body passes 170. A node that wants to be longer is two nodes: its
topic divides into a sibling leaf rather than being shortened to fit. A
leaf collection stays homogeneous in kind; an artifact of another kind
is filed where its kind lives. `est_tokens` stays within 2× of the
measured whole file, frontmatter included: the router sums these to
report context cost before work starts, so a lie here corrupts every
plan.

**Leaves and branches** (`knowledge-graph.branch-shape`). Review judges
this shape; no lint checks it.

- **A leaf holds one topic**, sized to what a typical task loads. A leaf
  whose separable topics are loaded independently divides into sibling
  leaves, each routable by its own `load_when` and linked to the others
  by `peers:`. A leaf whose topics are loaded together stays whole.
  Protocols, postures and the delegation files are leaves.
- **A branch is a menu.** A branch node (the router index, a hub, a
  subsystem or domain node, or a new thin parent) has a `## Leaves`
  section that lists each leaf with a one-line "load when", in the form
  `_schema.md` gives under "Body". Beyond the list it holds only the
  doctrine that binds every leaf and cannot live in any one of them.
- **A branch owns its menu**: which leaf answers which need, under the
  fact key `<slug>.menu`. A node that owns no fact, or a list without
  that routing information, is a link farm: delete it rather than pad
  it.

### 5. Compound

Nodes grow with the project. Add a fact when the code gains it; add a
sharp edge when it bites, dated; add a `load_when` trigger when a task
should have matched and didn't. A fact enters when the project meets it,
so the graph holds no theoretical facts.

Write every trigger in the forms a developer actually types, and in
forms of **three characters or more**: the router drops shorter tokens,
so `EF` can never route; write "entity framework" and "dbcontext"
instead. On a composed child the wording decides whether it is ever
reached at all, because descent tests the child's own vocabulary minus
its parent's: a trigger the family already carries sits on the parent,
adds nothing, and descends nobody. Give a child the words only it
answers to.

Compounding extends to being *wrong*: a recorded fact found false is
struck through and gets a dated **Correction** beside it, under the one
retraction rule in `skill.holistic-editing` (The append-only exception).

### 6. One graph, several depths

`libraries/`, `sources/`, `product/`, `architecture/`, `api/`, `data/`,
`prompts/`, `evaluations/`, `plans/`, `runbooks/`, `specs/`, and
`decisions/` are leaf collections of this one graph (`rule.knowledge`,
in `context-router`). Each leaf hangs off an owning node's edge; a leaf
without one is orphaned knowledge. Maintained project knowledge outside
`docs/graph/` is an input to corroborate and ingest.

### 7. Record where a secret lives

A knowledge page records where a secret lives, never the secret itself,
not even a partially masked copy: a "partially masked" token still leaks
its shape, length, and prefix, and the graph is committed, searchable,
and long-lived. Record a **pointer**: the secret manager path, the
env-var name, the vault key. The fact a reader needs is *where to look*,
and that is safe to own.

### 8. Status lives in frontmatter, in one vocabulary

Anything that can be open (an ADR, a spec, a risk row, a `deviation`
node) carries `status` and `status_date` in frontmatter, never in prose,
using the one lifecycle vocabulary and its required companions defined
in `docs/graph/_schema.md` ("Lifecycle status"); a body `## Status`
section is a pointer, and a body value that disagrees is a lint failure.
`graph-lint.py` checks nodes; `docs/graph/status-register.py` lints the
Tier-3 leaves and is the query surface (`--open --hotfix --summary`).
The schema is the vocabulary's home.

## Node body shape

Answer ONLY these, in this order: **what this is** (2–3 sentences) ·
**what you must know** (the owned facts, terse: bullets, tables, code) ·
**sharp edges** (what will bite, dated) · **where the code is**
(concrete paths, not descriptions of paths) · **neighbours** (why each
peer exists and when to cross to it).

## The linter

`docs/graph/` ships a linter, `docs/graph/graph-lint.py`, copied in from
`docs/graph/templates/knowledge-graph/graph-lint.py` and parameterized
on adoption. It makes the dedup rule real rather than aspirational. It
enforces the numbered rules in `docs/graph/_schema.md` ("The rules the
linter enforces"), which is their one home. Run it before committing any
graph change:

```sh
python3 docs/graph/graph-lint.py            # lint
python3 docs/graph/graph-lint.py --graph    # edges: -> requires, ~> composes
python3 docs/graph/graph-lint.py --plan "<task>"   # dry-run the router
```

A graph without a passing linter is a graph that has already started to
lie. Wire it into the verification gates.

An authoring or maintenance pass is done when the linter passes, every
new leaf resolves through an owning node's edge, and the facts that
motivated the pass each have exactly one home. Growth is demand-driven;
stop at the passing lint.

## When the graph is wrong

It will be; code moves and the graph lags. On a path the session-start
code-anchor line names, **the code wins on facts**: fix the node in the
same change. Elsewhere a node's facts about code are current as stated
(`rule.knowledge`). On every path **the node wins on contracts**: a code
violation of a recorded contract is a bug, not a doc update. When a task should have matched a node's
`load_when` and didn't, sharpen the trigger in the same commit.

## Reference files

- `docs/graph/skills/context-router.md` — how the graph is traversed.
- `docs/graph/skills/library-wiki.md` — the Tier-3 library-page
  discipline.
- `docs/graph/skills/validate-knowledge.md` — proving the graph is
  usable.
- `docs/graph/templates/knowledge-graph/` — the schema, linter, index,
  and node templates.
