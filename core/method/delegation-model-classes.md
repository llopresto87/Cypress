---
id: method.delegation-model-classes
tier: 2
kind: method
origin: seed
title: delegation model classes — the class and reasoning effort each step runs on, by step and by role and task kind
owns:
  - delegation.model-classes
  - delegation.effort
  - delegation.model-map
requires:
peers:
  - method.delegation
  - method.delegation-cycle-economy
  - method.delegation-light-variants
artifacts:
  - templates/agent.template.md
load_when:
  - "sonnet or opus, which model class"
  - "reasoning effort, low effort worker, model class per task kind"
  - "effort for this spawn, effort field in the agent definition"
  - "which model on this host, model map, provider, non-Anthropic model"
prevents: Every worker run on the most expensive model at full effort, or a cheap one handed authoring, review or a security surface it cannot carry.
est_tokens: 2464
---

## Route by model class

Read-only investigation and mechanical retrieval/normalization →
**investigation class** (draft artifacts are finalized by an authoring-class
librarian); authoring, implementation, judgment-heavy design, review, or
adversarial validation → **authoring class**. The one exception is a light
variant (`delegation.light-variants`, in `method.delegation-light-variants`): a light reviewer, a light tester
or a one-line-fix implementer runs small, mechanical work on the investigation
class (security surfaces excepted, below); every other authoring or review
step stays in its class. This **model class** lives in each agent's `model:`
frontmatter. It is a distinct axis from the **task tier** (T0–T3, kernel §0)
and the graph **load-tier** (the node `tier:` field): three independent axes
that share the word loosely; only the risk axis is written `T0–T3`, and
"model class" and "load-tier"/`tier:` name the other two.

**Two classes, four aliases.** The authoring class and the investigation
class are the only model classes. An agent's `model:` field names one of the
four aliases Claude Code reads natively: `opus` (authoring), `sonnet`
(investigation), `haiku` (investigation at low effort, whatever `effort:` says)
and `inherit` (the caller's model). Seed agents use `opus` and `sonnet`. On
every other host the alias names a class, and routing text names it in the
body's words, "authoring-class" or "investigation-class". The class a phase
uses stays owned by that phase's protocol node.

**The plant names the model once** (`delegation.model-map`). The model each
host runs for a class and an effort lives in `docs/graph/models.md`, which the
plant owns and fills once. Nodes, protocols and briefs name the class and the
effort and leave the model to that file. A spawn runs the model its map row
lists. A row still unfilled means the caller's model: the spawn omits the
model, and its routing evidence records `model: inherited (map row unfilled)`.
A filled row whose model does not resolve stops the spawn, which reports it.
Where the row is filled, the spawn passes that row's model and effort; letting
the caller's model stand in is right only for an unfilled row, and the routing
evidence says so. **A spawn never switches to another model or provider to get
past a rate or usage limit.** It waits and resumes (`delegation.continuation`), or
reports the limit as the blocker. A delegating worker passes the same rule and
its own model class into every brief it writes.
How each host reads the map is in that host's integration README.

**Effort refines the class; it is not a fourth axis.** Effort in this node is
*reasoning effort*, a host setting. It is not the owner-declared *effort level*
of a task, which `method.minimum-sufficient-work` owns. A host that accepts a
reasoning-effort setting runs a class at low, medium or high effort. Which
hosts accept one, and whether it is set per agent definition or per spawn, is
host policy, recorded under `delegation.effort` below. Where the host reads a
default effort from the agent's definition, that default is the baseline. A
spawn that departs from it, in model or in effort, records the departure and
its reason in the brief's routing evidence, the same place an overridden route
is recorded, so the delivery can see which budget each step ran on.

The class and effort each step kind runs on by default:

| Step kind | Class | Effort | Forced up to authoring class, high effort, when |
|---|---|---|---|
| Artifact discovery, extracting an earlier handback to a file | investigation | low to medium | the discovery itself has to decide something |
| Library research (`research-scout`) | investigation | medium | none: its draft is finalized by an authoring-class librarian |
| A mechanical gate run: a suite, the lints, writing the runbook record | investigation | low | the result is red: diagnosis goes to the authoring class (`protocol.recover`) |
| Spec contracts, architecture, rulings on a contract's reading, one-way doors, threat models, `devils-advocate` | authoring | high | already at the ceiling |
| The canonize librarian | authoring | low | the close-out ends a grow or a graft: high |
| A harvest's faithful-import review (`protocol.harvest`) | authoring | high | already at the ceiling |
| Any step on a security surface (the list under `delegation.light-variants`) | authoring | high | already at the ceiling |

A gate-running worker only runs the gates and asserts what they report,
failing closed on output it cannot read; the verdict on a red result belongs
to the authoring class.

### Effort (`delegation.effort`)

An agent definition's `effort:` key (`low`, `medium` or `high`) is the role's
default. Claude Code reads it from subagent frontmatter; the Agent tool's
per-spawn `effort` (v2.1.292+) overrides it, `CLAUDE_CODE_EFFORT_LEVEL`
overrides both, and a subagent with neither runs at the session's level,
`medium` by default on Opus 5.5 (code.claude.com/docs/en/sub-agents and
/model-config, retrieved 2026-11-09). Prime Agent takes the spawn's effort as
`thinking=`. opencode, Codex, GitHub Copilot: not recorded. No install
transform drops the key.

Each agent definition defaults to the effort of the step kind it mostly runs,
from the table above, and to `medium` where the table has no row
(`ui-ux-designer`, `data-ml`, `reliability`, `tool-smith`, `seed-installer`); `implementer` defaults to `low` (the role-and-kind table below):

| `effort:` | Agent (the step kind it mostly runs) |
|---|---|
| high | `orchestrator` (routing and rulings on a contract's reading), `architect` (spec contracts, architecture, rulings, one-way doors), `multi-agent-architect` (architecture), `security` (any step on a security surface; threat models), `pentest` (any step on a security surface), `devils-advocate` (adversarial validation), `legal` (rulings against a rule corpus), `growth-orchestrator` (the close-out that ends a grow) |
| medium | `tester` (RED for a new contract), `reviewer` (standard batch review), `product` (spec §3 and §9), `docs-librarian` (the canonize librarian), `research-scout` (library research), `growth-scout` (artifact discovery, low to medium) |

**Each spawn's effort follows its role and task kind** (the owner's decision of
2026-11-09, pending measurement). `brief.py --kind KIND[,KIND]
[--label LABEL]` prints and logs `effort: <value> (<reason>)` from the first
match, and the caller passes that value on the spawn: (1) `security`,
`--security-path` (other than a tester's `findings`), a harvest's faithful-import
review, diagnosing a red gate: `high`; (2) the row below (`by label`: the hardest increment label of
`delegation.effort-scale`, low or medium-low → low, medium → medium,
medium-hard or hard → high; a `first` review of trust-claimed files reads
`first-trust`; `at most` caps it); (3) the definition's default. The implementer caps at medium (owner, 2026-11-09): replays of a new flow's GREEN graded higher with each step up in effort, high only marginally above medium at half again the cost, and fix sets graded alike at low and medium, low at half the cost. A whole-increment GREEN defaults to low (measured on 2026-11-09): a replay of a whole increment at low cost about a third less than at medium and graded no worse, while a single feature built alone graded lower at low. Implementation runs at low (owner, 2026-11-10): every implementer kind is low and only an increment labelled hard is medium, because the review, the high-effort security pass and the findings tester are the quality net for low-effort implementation. Where several kinds fit, `fix`, `mechanical` and `amend` win over `trust` and `red-trust` (`--kind trust,fix` reads low).

| Role | Kind | Effort |
|---|---|---|
| implementer | `increment`: an increment batch | low; medium when labelled hard |
| implementer | `flow`: a new user-facing feature, flow or stateful contract, unlabelled | low |
| implementer | `trust`: new code on a trust surface | low |
| implementer | `fix`: a contained change or a review-fix set | low |
| implementer | `mechanical`: an edit, rename or one-line fix | low |
| tester | `red`: RED for an increment's contracts | by label |
| tester | `red-trust`: RED for a security or stateful contract, before its GREEN | high |
| tester | `findings`: RED for the review and security findings of a security pass, from the probe and control files that pass wrote | medium |
| tester | `amend`: amend one wrong test, rule on one test question, or carry a ruling pass's test amendments | low |
| reviewer | `first-trust`: the first review of a trust-surface increment | high |
| reviewer | `first`: an ordinary first review | medium |
| reviewer | `recheck`: a re-check of fixes | low |
| architect | `contract`: a new contract or boundary | high |
| architect | `ruling`: a ruling on one question | medium |
| architect | `wording`: a wording amendment | low |
| docs-librarian | `close-out`: the canonize close-out of an increment | low |
| docs-librarian | `grow-close-out`: the close-out that ends a grow or a graft | high |
| product | `ruling`: one product ruling | low |
| product | `spec`: spec §3 and §9 | medium |

The model class of each role and kind, beside it, is the role's `model:` until a measured trial moves a row, and the owner with it; `brief.py --kind` prints `model: <class>` and adds a `Model:` line only for a row unlike the role's `model:`.

| Role | Kind | Class |
|---|---|---|
| implementer | `increment` | opus |
| implementer | `flow` | opus |
| implementer | `trust` | opus |
| implementer | `fix` | opus |
| implementer | `mechanical` | opus |
| tester | `red` | opus |
| tester | `red-trust` | opus |
| tester | `findings` | opus |
| tester | `amend` | opus |
| reviewer | `first-trust` | opus |
| reviewer | `first` | opus |
| reviewer | `recheck` | opus |
| architect | `contract` | opus |
| architect | `ruling` | opus |
| architect | `wording` | opus |
| docs-librarian | `close-out` | opus |
| docs-librarian | `grow-close-out` | opus |
| product | `ruling` | opus |
| product | `spec` | opus |

On a host with no per-spawn setting, a derived value unlike the definition's
default adds `host applies: definition default <value>` to the logged line.
Departures fail closed: a rule-1 step goes to a `high` definition, or its
output takes a `high` review spawn (`security`, or `architect` for a contract
or ruling) before it lands; with neither it is a block.
