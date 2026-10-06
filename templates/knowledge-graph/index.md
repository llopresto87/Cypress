---
grown: false                       # set true by grow Phase 6; adopted plants stay false
plant:
  environment_class: <ephemeral-test | staging | real-production | mixed>
  commit_attribution: <none | trailer text>
  deliverable_language: <bcp47>
  comment_language: <bcp47>
---

<!--
Template: knowledge-graph/index.md
Lives at: docs/graph/index.md
Used: as Tier 1 — the hand-written map; the fallback the kernel's FIRST
MOVE names when the routed plan fails or looks wrong.
Fill the tables from the project's actual nodes. Keep it in sync as
nodes are added; the linter treats anything listed here as reachable.
-->

# The map: open when the route fails or looks wrong

<!-- pre-growth: grow removes this block -->
**Not grown yet.** Start from the installed `EXPERT_SEED_INSTALL_PROMPT.md`
(`/initialize` is only a tool adapter). `protocol.initialize` is the entry
fork: `protocol.grow` when there is source to scout, `protocol.from-scratch`
when the repository is empty.
<!-- /pre-growth -->

This is Tier 1, the only index, and the fallback map, not a first
read. The first move routes the task line instead (the kernel's FIRST
MOVE): the router suggestion the host injected, or

```sh
python3 docs/graph/graph-lint.py --plan "<your task>"
```

Open this page when the router fails, when a `!` notice leaves the plan
empty or wrong, or when the task explores the graph itself. Then match
your task against the triggers below, load the entry node plus the
transitive closure of its `requires:` edges, and load its `peers:` only
when the task crosses into them. `composes:` children are a menu, not a
closure: descend on a term of a child's `load_when:` or slug that the
parent lacks, never on body prose (`skills/context-router.md` §3).

If your hand-resolved node set disagrees with the routed plan, sharpen
the `load_when:` trigger at fault in the same commit. `--plan` is a
keyword heuristic; `skills/context-router.md` names the task kinds
where node ownership and this table outrank it.

## Start here by task shape

<!-- One row per common task phrasing → the entry node it should hit. -->

| Your task | Entry node(s) |
|---|---|
| "What is this? Where does X live?" | `{{root}}` |
| "Who should do this?" | `{{root}}.roster` or the relevant agent |
| Editing {{subsystem}} | `subsystem.{{name}}` |
| Working against {{framework or library}} | `expertise.{{slug}}` |
| Adding/changing data or schema | `data.{{model}}` |
| Anything about auth / tokens / permissions | `crosscut.{{auth}}` |
| Anything about secrets / credentials | `crosscut.{{secrets}}` |
| "How do I test this?" | `crosscut.{{testing}}` |
| Bring the stack up / deploy | `platform.{{deploy}}` |
| "Where does this config come from?" | `platform.{{config}}` |

## Method — how we work (machinery nodes, pre-filled; keep as installed)

The seed's method surface routes from here like any other knowledge.
Classify the task's tier first (kernel §0; depth: `method.tiers`), then
enter through the node that matches where the work stands. Full T3
sequence for new work: brainstorm → specify → grill → ingest-library →
test-first → verify → canonize → deliver.

| Where the work stands | Entry node |
|---|---|
| Which tier is this task? Execution paths | `method.tiers` |
| Who does this? Routing, model classes, briefs, delegation bounds | `method.delegation` · `method.delegation-model-classes` · `method.delegation-cycle-economy` · `method.delegation-briefs` · `method.delegation-sequencing` · `method.delegation-bounds` |
| Goal vague or contested | `protocol.brainstorm` |
| Goal clear, no executable spec covers it | `protocol.specify` |
| Spec exists; need the plan-of-record | `protocol.grill` |
| Need a new spec and a new plan-of-record in one pass, or classify design latitude; ask only in doubt | `protocol.specify-joint-pass` |
| About to write or change code | `protocol.test-first` |
| Introducing or refreshing a dependency | `protocol.ingest-library` |
| Increment claims "done" — run the gates | `protocol.verify` |
| Marking work closed, or a gate found a bug no gate would have caught | `protocol.verify-new-gates` |
| A check disagrees with its subject, a refactor/migration must preserve behavior, or a known defect must be tolerated | `protocol.verify-disagreement` |
| A worker, gate, or delegation failed | `protocol.recover` |
| Task completing — persist knowledge + tools | `protocol.canonize` (doctrine: `skill.toolcraft`; author: `agent.tool-smith`) |
| Session ending — the summary | `protocol.deliver` |
| No project graph yet, or major drift | `protocol.initialize` — the entry fork; it selects `protocol.grow` here because there is source to scout |
| Project does not exist yet | `protocol.initialize` — the same fork, selecting `protocol.from-scratch` because the repository is empty |
| Loading context minimally | `skill.context-router` |
| Authoring or linting graph nodes | `skill.knowledge-graph` |
| Engineering and design posture — the why | `method.engineering-posture` · `method.minimum-sufficient-work` · `method.decision-economy` · `method.host-parity` · `method.bounded-execution` · `method.design-posture` · `method.restrictive-policy` · `method.maintenance-contracts` · `method.design-governance` · `method.stewardship-posture` · `method.secrets-posture` · `method.release-posture` · `method.incident-posture` · `method.contract-posture` · `method.vcs-posture` · `method.prose-posture` |
| Prose a person will read: documentation, README, ADR or spec body, runbook, PR text, delivery summary, or a draft that reads like a model wrote it | `skill.humanizer` (procedure) · `method.prose-posture` (doctrine) |
| Fold lessons into the seed / carry the seed onto a plant | `protocol.harvest` / `protocol.graft` — user-sovereign: enter them only when the owner starts them; unprompted, only propose one |

Specialist agent nodes route by their own triggers; `method.delegation`
owns the roster table. The ids below are listed so graph-lint counts each
as a reachable entry point. Agents: `agent.orchestrator`,
`agent.architect`, `agent.implementer`, `agent.reviewer`,
`agent.tester`, `agent.security`, `agent.pentest`, `agent.reliability`,
`agent.data-ml`, `agent.product`, `agent.ui-ux-designer`,
`agent.docs-librarian`, `agent.research-scout`, `agent.devils-advocate`,
`agent.legal`, `agent.multi-agent-architect`, `agent.growth-orchestrator`,
`agent.growth-scout`, `agent.seed-installer`, `agent.tool-smith`.
Situational skills not routed above: `skill.adopt-existing` (adopting an
existing codebase), `skill.adr-writer` (recording a decision),
`skill.spec-author`, `skill.grill-planner`, `skill.brainstorm-socratic`
(user-facing) and `skill.brainstorm-internal` (no user in the loop),
`skill.holistic-editing`, `skill.library-wiki`,
`skill.research-and-ingest`, `skill.validate-knowledge`,
`skill.test-first`.

## The node table

<!-- Group by tier/kind. Keep ~tokens honest; they sum to the budget. -->

### Roots

| Node | Owns | ~tokens |
|---|---|---|
| `{{root}}` | project purpose, map, topology | {{n}} |

### Stacks / Expertise / Platform / Data / Cross-cutting / Domain

| Node | Owns | ~tokens |
|---|---|---|
| `stack.{{lang}}` | conventions, versions, build | {{n}} |
| `expertise.{{lib}}` | applicability, composition | {{n}} |
| `platform.{{x}}` | … | {{n}} |
| `data.{{model}}` | entities, migration story | {{n}} |
| `crosscut.{{concern}}` | … | {{n}} |

### Subsystems

| Node | Repo/path | Notes |
|---|---|---|
| `subsystem.{{name}}` | `{{path}}` | … |

## Cost discipline

- A **change** task should load a handful of nodes. More means it is
  really several tasks; split it and say so.
- A **trace** may follow many nodes, all on one path.
- **To compare sibling subsystems, read the shared node** that owns what
  they share.
- Loading the whole graph is the most expensive way to know the least.

## When the graph is wrong

It will be; the code moves and the graph lags.

1. **A fact the graph states is settled**: use it. Where the
   session-start code-anchor line names a node's paths as changed, the
   code wins on facts there: fix the node in the same change (kernel §3.2).
2. **The node wins on contracts**: a code violation of a recorded
   contract is a bug, not a doc update.
3. When a task should have matched a `load_when:` and didn't, sharpen
   the trigger.
4. Run `python3 docs/graph/graph-lint.py` before committing. It enforces
   the contract in `_schema.md` ("The rules the linter enforces").
