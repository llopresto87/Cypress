<!--
Template: knowledge-graph/index.md
Lives at: docs/graph/index.md
Used: as Tier 1 — the router every task opens first.
Fill the tables from the project's actual nodes. Keep it in sync as
nodes are added; the linter treats anything listed here as reachable.
-->

# The router — start every task here

This is Tier 1. It is the only index. Match your task against the
triggers below, load the entry node plus the transitive closure of its
`requires:` edges, and **do not** load its `peers:` unless the task
crosses into them.

The traversal is specified in `skills/context-router.md` and is
executable:

```sh
python3 docs/graph/graph-lint.py --plan "<your task>"
```

If your hand-resolved node set disagrees with that output, one of you
is wrong — usually a `load_when:` trigger needs sharpening. Fix it in
the same commit. (`--plan` is a keyword heuristic, not an oracle;
`skills/context-router.md` owns the list of task kinds on which you
should trust node ownership and this table over it.)

---

## Start here by task shape

<!-- One row per common task phrasing → the entry node it should hit. -->

| Your task | Entry node(s) |
|---|---|
| "What is this? Where does X live?" | `{{root}}` |
| "Who should do this?" | `{{root}}.roster` or the relevant agent |
| Editing {{subsystem}} | `subsystem.{{name}}` |
| Adding/changing data or schema | `data.{{model}}` |
| Anything about auth / tokens / permissions | `crosscut.{{auth}}` |
| Anything about secrets / credentials | `crosscut.{{secrets}}` |
| "How do I test this?" | `crosscut.{{testing}}` |
| Bring the stack up / deploy | `platform.{{deploy}}` |
| "Where does this config come from?" | `platform.{{config}}` |

---

## Method — how we work (machinery nodes, pre-filled; keep as installed)

The seed's method surface routes from here like any other knowledge.
Classify the task's tier first (kernel §0; depth: `method.tiers`), then
enter through the node that matches where the work stands. Full T3
sequence for new work: brainstorm → specify → grill → ingest-library →
test-first → verify → canonize → deliver.

| Where the work stands | Entry node |
|---|---|
| Which tier is this task? Execution paths | `method.tiers` |
| Who does this? Routing, model classes, briefs, delegation bounds | `method.delegation` |
| Goal vague or contested | `protocol.brainstorm` |
| Goal clear, no executable spec covers it | `protocol.specify` |
| Spec exists; need the plan-of-record | `protocol.grill` |
| About to write or change code | `protocol.test-first` |
| Introducing or refreshing a dependency | `protocol.ingest-library` |
| Increment claims "done" — run the gates | `protocol.verify` |
| A worker, gate, or delegation failed | `protocol.recover` |
| Task completing — persist knowledge + tools | `protocol.canonize` (doctrine: `protocol.toolcraft`) |
| Session ending — the summary | `protocol.deliver` |
| No project graph yet, or major drift | `protocol.grow` (`protocol.initialize` is the tool adapter) |
| Project does not exist yet | `protocol.from-scratch` |
| Loading context minimally | `skill.context-router` |
| Authoring or linting graph nodes | `skill.knowledge-graph` |
| Engineering and design posture — the why | `method.engineering-posture` · `method.design-posture` · `method.stewardship-posture` |
| Fold lessons into the seed / carry the seed onto a plant | `protocol.harvest` / `protocol.graft` — **user-sovereign, never automatic** |

Specialist agent nodes route via their own triggers; `method.delegation`
owns the roster table. The full roster: `agent.orchestrator`,
`agent.architect`, `agent.implementer`, `agent.reviewer`,
`agent.tester`, `agent.security`, `agent.pentest`, `agent.reliability`,
`agent.data-ml`, `agent.product`, `agent.ui-ux-designer`,
`agent.docs-librarian`,
`agent.research-scout`, `agent.devils-advocate`,
`agent.multi-agent-architect`,
`agent.growth-orchestrator`, `agent.growth-scout`,
`agent.seed-installer`. Situational skills not routed above:
`skill.adopt-existing` (adopting an existing codebase),
`skill.adr-writer` (recording a decision), `skill.spec-author`,
`skill.grill-planner`, `skill.brainstorm-socratic`,
`skill.from-scratch-bootstrap`, `skill.holistic-editing`,
`skill.library-wiki`, `skill.research-and-ingest`,
`skill.validate-knowledge`, `skill.test-first`.
`harvest` and `graft` are user-sovereign — never enter them unprompted.

---

## The node table

<!-- Group by tier/kind. Keep ~tokens honest; they sum to the budget. -->

### Roots

| Node | Owns | ~tokens |
|---|---|---|
| `{{root}}` | project purpose, map, topology | {{n}} |

### Stacks / Platform / Data / Cross-cutting / Domain

| Node | Owns | ~tokens |
|---|---|---|
| `stack.{{lang}}` | conventions, versions, build | {{n}} |
| `platform.{{x}}` | … | {{n}} |
| `data.{{model}}` | entities, migration story | {{n}} |
| `crosscut.{{concern}}` | … | {{n}} |

### Subsystems

| Node | Repo/path | Notes |
|---|---|---|
| `subsystem.{{name}}` | `{{path}}` | … |

---

## Cost discipline

- A **change** task should load a handful of nodes. More means it is
  really several tasks; split it and say so.
- A **trace** may follow many nodes along one path, but never a node
  off that path.
- **Never load two sibling subsystem nodes to compare them.** What they
  share belongs in a shared node; read that.
- Loading the whole graph is the most expensive way to know the least.

## When the graph is wrong

It will be; the code moves and the graph lags.

1. **The code wins on facts** — fix the node in the same change.
2. **The node wins on contracts** — a code violation of a recorded
   contract is a bug, not a doc update.
3. When a task should have matched a `load_when:` and didn't, sharpen
   the trigger.
4. Run `python3 docs/graph/graph-lint.py` before committing. It enforces
   unique fact ownership, resolvable and acyclic edges, reachability,
   artifact/library edge resolution, and that no version pin leaks out
   of `docs/graph/libraries/`.
