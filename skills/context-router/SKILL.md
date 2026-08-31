---
name: context-router
description: 'Resolve the minimum set of knowledge-graph nodes needed for a task before reading any source file. Use at the START of every non-trivial task once a project has a knowledge graph — when changing a subsystem, tracing a bug, planning work, answering a question about how something works, or onboarding. This is the mechanism that keeps a large or multi-repo codebase inside a context window: it decides what to load, what to deliberately skip, and forces the agent to declare both before working. Pairs with the knowledge-graph skill, which builds and lints the graph this one traverses.'
id: skill.context-router
tier: 2
kind: skill
origin: seed
title: context-router — the knowledge rule and the traversal that resolves the minimal node set for a task
owns:
  - rule.knowledge
  - context-router.method
  - context-router.declaration
requires:
  - skill.knowledge-graph
peers:
  - skill.validate-knowledge
load_when:
  - "what should I load for this task"
  - "resolve the minimal node set before working"
  - "route a task through the knowledge graph"
  - "declare loaded and skipped nodes"
  - "orient in a large codebase without bulk-reading"
  - "context budget for a change"
artifacts:
  - templates/prompts/graph-session-bootstrap.md
  - templates/knowledge-graph/_schema.md
  - templates/knowledge-graph/index.md
est_tokens: 2100
---

# context-router

A large codebase does not fit in a context window, and loading all of
it makes an agent worse, not better — a model that has read everything
has no signal about what matters. This skill replaces "read around
until it feels familiar" with a traversal that terminates and that you
can defend.

This skill owns the knowledge rule — the graph is the source of truth
for *structure and capability*, loaded minimally — and the traversal
algorithm that makes the rule executable.

## The knowledge rule

The project keeps **one LLM-maintained knowledge system** at
`docs/graph/`: Tier 1 routes, Tier 2 nodes own concise facts, Tier 3
leaf collections hold source-backed depth (libraries, provenance,
product, architecture, APIs, data, prompts, evaluations, plans,
runbooks, specs, decisions, tools). Never parallel doc systems.

- **Load minimally, and declare it.** Resolve the minimal node set from
  the router — entry nodes plus `requires:` closure — and declare what
  you loaded and deliberately skipped. Never bulk-read to get oriented;
  the graph is the orientation. The algorithm below is the full form of
  this obligation; the delegation-boundary form is
  `docs/graph/templates/prompts/graph-session-bootstrap.md`.
- **One home per fact.** Every fact lives in exactly one node's
  `owns:`; everything else links. Duplicated facts rot asymmetrically.
  `graph-lint.py` enforces unique fact-keys, resolvable acyclic edges,
  and no version pin outside its owning library page.
- **Graph before code, ahead of memory.** Memory of APIs and versions
  is unreliable; the graph is local and source-grounded. No wiki page
  for a library you're about to use → run `ingest-library`.
- **The graph compounds.** Record facts when code gains them, sharp
  edges when they bite, `load_when:` triggers when routing missed.
  Never fabricate a fact, version, or URL — write "not recorded".

Authoring and maintaining what this rule loads is `skill.knowledge-graph`
(`docs/graph/skills/knowledge-graph.md`) — read its node contract once
(the `_schema.md` the graph was built from); dependency leaves are
`skill.library-wiki`. Prefer a configured Context7 / DeepWiki /
`llms.txt` MCP server for *fetching* upstream content. If the project
has no graph yet, build one via `adopt-existing` / `knowledge-graph`
first; until then, fall back to reading the README and the
plan-of-record, and say you did.

## The algorithm

### 1. Classify the task in one sentence

Say what kind of work it is before deciding what to read. The four
kinds route differently:

| Kind | Example | Entry |
|---|---|---|
| **Question** | "how does auth work?" | The node that *owns* the fact. Answer with citations. Read no code unless the node is wrong. |
| **Change** | "add a field to X" | The owning subsystem node + its required closure. |
| **Trace** | "why is this endpoint 401-ing?" | Every node on the request/data path. Follow `peers` deliberately — this is the one kind that legitimately crosses them. |
| **Plan** | "rebuild the deploy pipeline" | The plan-of-record + the relevant platform/infra nodes. |

### 2. Resolve entry nodes

Open the graph's router index (Tier 1) and match the task against each
node's `load_when:` triggers. Prefer the most specific match. A task
naming a path resolves to that subsystem's node; a task naming a
concept resolves to the node that `owns` it.

If nothing matches, you have found a gap in the graph. Say so, fall
back to the root node, and note it for the graph's maintainer to fix.

**Watch for aliased names across layers.** When a subsystem answers to
more than one name — a repo or folder name that differs from its
product name, its package/artifact name, and its internal code name — a
task that types one alias can silently fail to match a node keyed to
another, and neither `load_when` matching nor a `grep` sees the miss.
The Tier-1 router index must carry an explicit **naming-divergence
note** listing the aliases for each such subsystem, so routing and
search are not blind to any one of them. When you hit an unlisted alias,
add it to that note in the same change (like sharpening a `load_when`
trigger).

### 3. Take the required closure

Load each entry node, then transitively load every node in its
`requires:` list. This closure is what you cannot be correct without.
It is small by construction — if it is not, the graph is mis-modelled
and should be fixed rather than worked around.

### 4. Do not take `peers`

`peers:` are the boundaries you are choosing not to cross. Load a peer
only when the task explicitly crosses into it — and when you do, say
why. The one exception is a **trace**: following a request or a message
across subsystems is exactly what `peers` edges are for.

### 5. Declare before you work

Print the resolved set. This is not ceremony — it is the artifact that
lets a reviewer catch a bad load before it becomes a bad change.

```
Task: add field <F> to <entity>                              [change]

LOAD (N nodes, ~T tokens)
  <entry node>          (entry)
  <required node>       (requires)
  <required node>       (requires)

NOT LOADED (peers)
  <peer node>   — owns X; not touched
  <peer node>   — holds a copy of Y; cross only if the change must reach it

Tier-3 to open on demand
  <library page / spec / ADR> — if the detail is needed
```

Then, and only then, open source files — and only the ones the loaded
nodes name.

### 6. Widen honestly, never silently

If mid-task you discover you need a node you did not load, load it and
say so ("Widening: loading <node> — the change is not local because
…"). Silent widening is the failure this skill prevents. So is
stubbornly working without a node you need in order to look
disciplined. Both are worse than "I was wrong about the boundary."

## Dry-run it

The graph router is executable and **must run inside every spawned worker
session** — that requirement travels as the canonical block every
delegation brief embeds (`docs/graph/templates/prompts/graph-session-bootstrap.md`:
run `--plan` with the exact delegated task, load the closure, declare,
return the output as route evidence); this skill owns the traversal
*algorithm* above, not a second copy of that block. Dry-run your own
hand-resolved set against the tool:

```sh
python3 <graph-tools>/graph-lint.py --plan "add a field to X"
```

If the two differ, one of you is wrong — usually a `load_when:` trigger
needs sharpening, a cheap permanent fix.

**`--plan` is a keyword heuristic, not an oracle.** It ranks nodes by
weighted term overlap; it does not reason about a request path or a
false premise. Trust it for a single-subject change or question, and
as a floor everywhere. But on four kinds of task, trust your own
reasoning over its output:

- **Traces** — the right nodes are the hops on the path, which keyword
  overlap cannot infer.
- **False-premise questions** ("confirm we use X") — the correcting
  node may share no words with the wrong assumption; ask which node
  would own the truth.
- **Policy questions** — these have one owning node; `--plan` may pad
  the set. Prefer the single owner.
- **Compound / multi-topic tasks** — a task description that bundles
  several distinct topics dilutes each topic's distinctive terms below
  the keyword threshold, so the ranking can resolve to the *wrong* node
  and specialist set entirely, not merely a partial one. Probe each
  sub-topic separately, or explicitly discount the output for a task you
  know is compound.

## Stopping rules

Stop loading when any of these is true:

- The required closure is exhausted.
- You can state the change you are about to make and name the contract
  it must not break.
- The next node you would open is a `peer` and the task does not cross
  into it.

Do **not** stop merely because you have loaded "enough" files. The
closure is the rule, not your comfort.

## Cost discipline

- **Within the loaded scope, retrieve progressively.** The closure
  names the files; it does not license reading them whole. Indexes,
  headings, symbols, and diffs before regions; excerpts before full
  files; the complete source only when exactness demands it. Query in
  order of precision — exact identifier, exact phrase, constrained
  keyword, scoped filters, semantic search, broad exploration last —
  and let one authoritative source decide a question unless evidence
  conflicts or the consequence of error justifies corroboration
  (the retrieval posture: `docs/graph/method/engineering-posture.md`).
- A **change** task should load a handful of nodes. If it needs many,
  it is really several tasks; split it and say so.
- A **trace** may legitimately load many nodes along one path — but
  never a node off that path.
- **Never load two sibling subsystem nodes "for comparison."** If they
  are near-identical, what they share belongs in a shared node; read
  that instead. Needing a second sibling to infer a convention means
  the convention is missing from where it should live — add it there.

## Anti-patterns

- **Bulk-reading a subsystem to get oriented.** The graph is the
  orientation. Confirming a path with `ls`/`grep` is fine; reading
  twenty files to build a mental model is the thing this skill stops.
- **Loading the whole graph "to be safe."** Full load is a summary
  that displaces the code you actually need — the most expensive way
  to know the least.
- **Treating `load_when` as documentation.** It is an index. When a
  task should have matched a node and didn't, fix the trigger in the
  same change.
- **Skipping the declaration because the task is small.** The
  declaration costs one paragraph and is the only record of what you
  did not read.

## Reference files

- `docs/graph/skills/knowledge-graph.md` — builds and lints the graph.
- `docs/graph/templates/knowledge-graph/_schema.md` — the node contract.
- `docs/graph/templates/knowledge-graph/index.md` — the router-index template.
- the kernel (`AGENTS.md`) — the context-budget rule this skill implements.
