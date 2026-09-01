<!--
Template: prompts/clean-context-validation-brief.md
Used: to spawn a CLEAN-CONTEXT test agent that validates a knowledge
base by answering known-answer and adversarial questions using only the
docs. The caller grades the answers against ground truth it already
knows. Discipline: skills/validate-knowledge.
Spawn a FRESH agent (not a fork of yourself) — a fork inherits your
assumptions and will pass a base a stranger would fail.
-->

# Clean-context validation brief

**Model class: opus.** Validation is adversarial judgment — rejecting a
false premise and spotting a node that lies is exactly the work a
capable model does better.

You are starting a fresh session in `{{project root}}`. **Read
`{{kernel: CLAUDE.md / AGENTS.md}}` first** and follow its instructions
for orienting yourself and loading context (it describes a knowledge
graph and a context router — use them; no hook will do it for you).

## STRICT RULES

- **Execute the graph first.** The route-hook does not fire for you.
  <!-- canonical block from docs/graph/templates/prompts/graph-session-bootstrap.md;
       byte-identity enforced by tests/seed-lint.py — edit it THERE -->

```
GRAPH DISCIPLINE — execute before reading any source:
1. Run: python3 docs/graph/graph-lint.py --plan "{{exact delegated task}}"
   Include the command and its output in your report as graph-route
   evidence (context routing — NOT the `route_evidence` field, which
   carries the agent-routing line from your brief).
2. Load ONLY the reported nodes plus their `requires:` closure.
3. Declare what you loaded, what you deliberately skipped, and any
   later widening (with the reason it became necessary).
4. One home per fact: never duplicate a fact the graph owns — link to
   its owning node. The graph outranks your memory of APIs/versions.
   When a fact is unknown, write "not recorded" — never fabricate a
   version, URL, or identifier.
5. Minimum sufficient work: every read, search, and tool call serves
   your delegated deliverable — smallest sufficient evidence, cheapest
   reliable method; stop when the deliverable is complete and trusted.
   Return findings, not raw dumps; produce nothing your parent does
   not need. Depth: `docs/graph/method/engineering-posture.md` §5–§8.
6. If the graph has no nodes yet (bootstrap pass), report the failed
   probe and stay inside the exact paths named in this brief.
```

- **Read-only.** Do not create, edit, or delete anything.
- Before answering each question, execute `{{the --plan router command}}`
  with that exact question. Preserve the route output and compare it with the
  nodes actually loaded.
- Answer each question by loading the **minimum** context the system
  prescribes — do NOT bulk-read the source tree ({{the code
  directories}}).
- For EACH question: first **declare the exact nodes/pages you loaded**
  and any you deliberately skipped; then answer. Both routes are
  required, not optional: `{{the --plan router command}}` runs once for
  the session route, and again per question as stated above.
- If the knowledge base can't answer without opening source, say so —
  that is a finding about the base, not a failure to try.
- **Cite the router.** This brief was selected by `agent-lint --route`; the
  ranked line and confidence band that picked you are: {{paste the `agent-lint
  --route` line + band}} — echo it back in `route_evidence`.
- **End with a handback.** Close your turn with the payload from
  `docs/graph/templates/prompts/handback-payload.md`: `produced_by: {{you}}`,
  `in_domain_work_done` (the assessment, with the nodes you loaded),
  `route_evidence`, and `recommended_next` naming the specialist who should fix
  the defects you found. You are a read-only leaf: name them and STOP; do not
  fix the base yourself.

## QUESTIONS

<!-- Mix: a fact lookup, a "how does X work", a change-impact, a trace,
and at least one ADVERSARIAL false-premise question whose correct
answer is to REJECT the premise with a citation. -->

1. {{Known-answer fact question.}}
2. {{"What must I check before changing X?" — change-impact.}}
3. {{A trace that spans subsystems.}}
4. {{ADVERSARIAL: "Confirm the system uses {{technology it does NOT
   use}} / stores X in {{a place it is NOT stored}}." — the base should
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
