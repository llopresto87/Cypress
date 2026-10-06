---
id: method.delegation
tier: 2
kind: method
origin: seed
title: delegation — the specialist roster, mechanical routing, shared spec authoring, and the sibling leaves
owns:
  - delegation.roster
  - delegation.routing
  - delegation.spec-authoring
requires:
peers:
  - method.delegation-model-classes
  - method.delegation-cycle-economy
  - method.delegation-briefs
  - method.delegation-sequencing
  - method.delegation-bounds
  - method.tiers
load_when:
  - "who should do this, which specialist, which agent"
  - "route the task, agent routing, roster"
prevents: Specialists picked by whoever is asking, with no ranked route, no named knowledge-or-judgment gap, and no shared sign-off on a spec.
est_tokens: 1135
---

# Delegation — the team and routing

The host session is the **orchestrator**: it routes, plans, briefs,
verifies, communicates, and accepts. Whether it also *does* is decided
by the task's tier (`method.tiers`). Specialists live in
`docs/graph/agents/` — each a fully-formed system prompt, projected
into the host tool's agent directory at install time. Invoke one by
spawning a clean-context worker with a purpose-made brief; persona
simulation in the chat is not delegation.

## The roster

A *specialist* is a member of the shipped roster below; an *expert* is one
you commission for this project (`delegation.routing`, below), and it joins
only the project's roster. The words are otherwise interchangeable.

| Specialist            | When to call                                                      |
|-----------------------|-------------------------------------------------------------------|
| `orchestrator`        | First contact; any request spanning more than one specialist.     |
| `architect`           | System boundaries, ADR-worthy decisions, contracts between modules. |
| `implementer`         | GREEN-phase code once a spec and failing tests exist.             |
| `reviewer`            | Auditing a diff against spec, plan, tests, graph.                 |
| `tester`              | Spec→test translation, RED phase, gates, regression corpus.       |
| `security`            | Threat models, auth, secrets, supply chain, AI abuse.             |
| `pentest`             | Hands-on authorized penetration testing; reproduce → fix → re-verify. |
| `reliability`         | Deploy, observability, rollback, capacity, cost; infra from scratch. |
| `data-ml`             | Datasets, pipelines, model selection, evaluation, synthetic data. |
| `product`             | User outcome, UX, acceptance criteria, accessibility.             |
| `ui-ux-designer`      | Interface/interaction design: flows, states, tokens, components, heuristics audits. |
| `docs-librarian`      | `docs/graph/` health, fact ownership, wiki leaves, catalogs, close-out. |
| `research-scout`      | Internet research; ingest libraries/specs into the wiki.          |
| `devils-advocate`     | Hostile pass over a *finished* claim-bearing deliverable; refutes from primary sources. |
| `legal`               | Regulatory compliance: corpus-bound legal reasoning, four-part findings, citation ledger. |
| `multi-agent-architect` | Agent-topology design/review: delegation bounds, tool contracts, fail-closed gates, evals, cost budgets. |
| `growth-orchestrator` | Growth DNA: conducts grow/adopt/from-scratch end to end.          |
| `growth-scout`        | Read-only per-boundary evidence gathering for graph authors.      |
| `tool-smith`          | A plant operation done by hand enough times to have earned a durable, tested tool; owns the bar and refuses below it. Builds plant tools only. |
| `seed-installer`      | Additive seed/adapter install; verifies the host loads the kernel. |

## Route mechanically first

Before spawning, run `python3 docs/graph/agent-lint.py --route "<task>"`
and cite the ranked line + confidence band in the brief. It is a
keyword heuristic, not an oracle: reason over it, and record why if
you override a HIGH-band pick. Work split by area across several
workers (one review divided by surface, say) is routed area by area,
each with its own task statement, because one run over the whole picks
for the whole.

**On LOW/NONE, ask what the gap *is* before you fill it.** The band says
no specialist matched; it does not say what was missing.

- **Knowledge** — a language, runtime, framework, library, or platform
  nobody on the roster is written for. The answer is an `expertise.*`
  node, authored or extended from
  `docs/graph/nodes/_expertise.template.md`, which the router composes
  into whichever worker's task names it: the specialist you already have
  does the work knowing the domain. No spawn, no roster row, no
  registration. This is the common gap and the default answer.
- **Judgment that needs its own context** — different `tools`, a
  different `model` class, an adversarial `stance`, or `isolation` from
  the caller's context. Those four are what a node cannot be, and they
  are the whole warrant for an agent. Check `agent-corpus/` for the role
  first — where present, harvested on demand — before authoring from
  scratch, then spawn an authoring-class agent-definition author to
  create the missing expert from `docs/graph/templates/agent.template.md`,
  grounded in the project's version-pinned facts (the `stack.*` node,
  its `expertise.*` node, the library wiki), because a remembered
  version may not be the one the project uses.

The *new expert's* `model:` frontmatter is `sonnet` (the investigation
class) if it only investigates, `opus` (the authoring class) if it
authors; the definition author itself is always authoring class. A
definition authored mid-session is not yet a spawnable type: see
`delegation.harness-registration` (`method.delegation-bounds`) before
delegating to it.

## Spec authoring is shared

`product` writes the user-facing layer, `architect` the functional
contracts, `tester` the executable encoding. A spec is finished when
all three signed off on the same document.

## Neighbours

- `method.tiers`: decides whether to delegate at all; cross when
  classifying, before choosing workers.
- `method.delegation-model-classes`: load when sonnet or opus, which
  model class.
- `method.delegation-cycle-economy`: load when how many increments per
  spawn, batch size.
- `method.delegation-briefs`: load when spawn a worker, write a
  delegation brief.
- `method.delegation-sequencing`: load when spawn order, parallel or
  sequential, which spawn waits for which.
- `method.delegation-bounds`: load when delegation depth, allowlist, can
  this agent spawn.
