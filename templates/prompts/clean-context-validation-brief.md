<!--
Template: prompts/clean-context-validation-brief.md
Used: to spawn a clean-context test agent that validates a knowledge
base by answering known-answer and adversarial questions using only the
docs. The caller grades the answers against ground truth it already
knows. Discipline: skills/validate-knowledge.
Spawn a fresh agent: a fork of yourself inherits your assumptions and
passes a base a stranger would fail.
Model class: opus (the authoring class): validation is adversarial
judgment, and rejecting a false premise or spotting a node that lies is
the work a capable model does better.
-->

# Clean-context validation brief

You are starting a fresh session in `{{project root}}`. **Read
`{{kernel: CLAUDE.md / AGENTS.md}}` first** and follow its instructions
for orienting yourself and loading context: it describes a knowledge
graph and a context router, and you run both yourself.

## Rules

- **Execute the graph first; these blocks are your routing.**
<!-- canonical blocks from docs/graph/templates/prompts/graph-session-bootstrap.md;
     tests/seed-lint.py holds them byte-identical, so edit them there -->

```
GRAPH DISCIPLINE — execute before reading any source:
1. Run: python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}"
   Report it in `graph_route:` as ids, never the router's output.
2. Load ONLY the reported nodes plus their `requires:` closure.
   Everything else a loaded node lists (leaves, children, links,
   neighbours) is a menu: open an item only when its one-line
   "load when" serves your task, and list the rest as skipped.
3. Before reading the files you will touch, check that each stack
   element they use (extension, path, manifest, lockfile) and their
   area has an `expertise.*` node, owning node or `libraries/` page in
   the route; for each one missing, run `--plan "<that element>"` and
   load what it reports. Declare in `graph_route:` what you loaded,
   skipped, and widened (with the reason).
4. Link to the node that owns a fact; do not restate it. The graph
   outranks your memory of APIs and versions. A fact the graph states
   is settled: use it as stated; re-deriving or re-checking it spends
   what the graph saves. Facts about code are current only where your
   brief carries a code-anchor line saying no code changed; otherwise
   check the code facts you rely on against the code. An unknown fact
   is "not recorded": never invent a version, URL or identifier.
5. Every read, search and tool call serves the deliverable; stop when
   it is complete and trusted. Read a spec by contract:
   `python3 docs/graph/spec-lint.py --slice --refs SLUG...`, then open
   only the §6/§7 headings it cites. Return only what your parent
   needs (`method.minimum-sufficient-work`).
6. Leave shared git state alone: `git stash`, `checkout`, `restore`,
   `reset` and `clean` move other writers' uncommitted files. Take a
   baseline by copying the file or `git show HEAD:<path>`
   (`delegation.wave-baseline`).
7. No graph nodes yet (bootstrap pass): report the failed probe and
   stay inside the paths this brief names.
```

```
COMPANION:
- Routed by: {{the protocol phase, the agent-lint --route line and band,
  or the override rationale}}. brief.py logged it with your spawn_id, role
  and effort, so your handback starts at `status:`. At a LOW/NONE band,
  name the gap in `out_of_domain_needed`: the fitting specialist, or the
  expertise the graph still needs.
- End your turn with the HANDBACK payload; at an out-of-domain boundary
  name the specialist in `recommended_next`. Past the soft target, write
  the overflow note as you work and name it (handback-payload.md, Rules).
```

- **Read-only.** Use commands that only inspect (`ls`, `grep`, `wc`,
  `git log`, reading files); anything that changes state, in files, Git
  or elsewhere, is outside this brief.
- **Route twice.** Run `{{the --plan router command}}` once for the
  session route, and again before each question with that exact
  question. Preserve each route output and compare it with the nodes
  actually loaded.
- Answer each question by loading the **minimum** context the system
  prescribes. The source tree ({{the code directories}}) stays closed:
  if the knowledge base can't answer without opening source, say so,
  because that is a finding about the base, not a failure to try.
- For each question: first **declare the exact nodes/pages you loaded**
  and any you deliberately skipped; then answer.
- **Your handback carries the assessment.** `in_domain_work_done` holds
  it, with the nodes you loaded. As a read-only leaf you ONLY name, in
  `recommended_next`, the specialist who should fix the defects you
  found; the fixing is theirs.

## QUESTIONS

<!-- Mix: a fact lookup, a "how does X work", a change-impact, a trace,
and at least one adversarial false-premise question whose correct
answer is to reject the premise with a citation. -->

1. {{Known-answer fact question.}}
2. {{"What must I check before changing X?" — change-impact.}}
3. {{A trace that spans subsystems.}}
4. {{ADVERSARIAL: "Confirm the system uses {{technology it does not
   use}} / stores X in {{a place it is not stored}}." — the base should
   let you reject this.}}

## Then a SYSTEM ASSESSMENT

- Did the kernel orient you and point you to the router/graph? How many
  nodes did you load in total?
- Did you ever open a source file or bulk-read the tree?
- For each adversarial question: did the base give you enough to
  **reject** the false premise, or did you get misled?
- Did any node contradict another, state something that seems wrong, or
  point somewhere that didn't deliver? Did `--plan` agree with your
  hand-picked sets?
- One sentence: could a newcomer reproduce your answers from the base
  alone?

Be blunt. A negative finding is worth more than praise — every wrong
answer or missed rejection is a defect in the base for the caller to
fix.
