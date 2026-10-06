# Suggested skill: evolve-agent-charter

> Optional procedure: an agent charter (a roster agent, a plant's own
> `origin: project` expert, or a role selected from `agent-corpus/`) behaved
> wrongly, and the fix is an edit to the charter. **Composes**
> `templates/agent.template.md` (the charter's sections and frontmatter),
> `skills/holistic-editing/SKILL.md` (the edit integrates into the whole
> charter), `protocols/deliver.md` (the routing-attribution assertion and the
> metrics that surface a misroute), `protocols/canonize.md` (where a lesson
> lands), and `core/method/stewardship-posture.md` (§6: a lesson or an owner
> rule lives in the graph, never in a charter's own log or in harness memory)
> by reference. What it adds is the table from an observed symptom to the one
> charter section to edit, the edit, and the check that proves it, applied one
> deficiency at a time.

**Instantiate by supplying:** `<CHARTER>` (the agent file, at
`docs/graph/agents/<name>.md` in a plant), `<SYMPTOM>` (what the agent did,
with the task text and the handback or transcript that shows it),
`<AGENT_LINT>` (the plant's `docs/graph/agent-lint.py`), and `<GOLDEN>` (the
plant's golden routing corpus, `docs/graph/agents/_routes.golden.tsv`, read
by `agent-lint --eval`).

## When to apply

- `deliver`'s routing-attribution assertion flagged out-of-domain authoring or
  an unexplained override for this agent.
- The agent was selected for a task it should not own, or was not selected
  for one it should.
- The agent used a tool its role should not need, gave wrong advice for a
  scenario, missed a failure mode, or failed to hand off.
- The owner corrected the same behaviour of this agent more than once.
- `deliver`'s metrics show recurring route overrides, or recurring `LOW`
  route bands, for one kind of task.

## 1. Name one deficiency, with its evidence

State the single deficiency this edit fixes and the evidence for it: the task
text, the routing line (`<AGENT_LINT> --route "<task>"` output), the
handback, or the owner's words. One deficiency per edit. When several are
observed, fix the most damaging and file the rest.

No evidence, no edit. A charter edited on speculation ("it might also need
...") grows triggers that steal neighbours' work and rules that nobody can
trace to a failure.

## 2. Find the section from the symptom

| symptom | section of `<CHARTER>` | edit | check |
|---|---|---|---|
| selected for tasks it should not own | `routing_triggers`, and the "Use whenever" clause of `description` | replace a generic phrase with the distinctive phrases of the work it does own; never add a broader one | `<AGENT_LINT> --route` on the misrouted task no longer selects it; `--eval` holds every class |
| not selected for a task it should own | `routing_triggers` | add the phrase a developer would type for that task, distinct from every neighbour's triggers | `--route` on the task selects it; add the task to `<GOLDEN>` as a `contract` row, because the trigger was written from it (a `paraphrase` row is written only by someone who has not read the triggers) |
| uses tools the role should not need | `tools:` in frontmatter | remove the excess grant (or add a missing one); keep `can_delegate` true exactly when the spawn tool is granted | `<AGENT_LINT> --lint` passes |
| acts outside its domain | "When to invoke" boundary line, or "Neighbours & scope boundary" | add the explicit exclusion and the agent that owns that work | the named agent exists in the roster (`--lint`); `--route` on the out-of-domain task selects the owner |
| does not hand off | "Handback" section, and `recommended_next` guidance | name the boundary and the specialist to recommend | walk the failing task: the charter now names where to stop |
| gives wrong advice for a scenario | "How you work": the decision path for that scenario | add or correct the if-this-then-that path | walk the failing scenario through the new text |
| misses a failure mode | the sharp edges of the node the agent serves (the fact's home), cited from "How you work" if critical | add the symptom, cause and fix to the node after checking it is not already there | the fact has one home (`graph-lint.py` passes); the charter cites it |
| repeated owner correction | the node that owns the rule's topic: this charter's own section for a rule about how this role behaves, the plant's operator node for a plant working rule | file it through a session record (`stewardship-posture` §6), never in a charter-local log or harness memory | the next session loads the rule from the graph |
| a way of working proved itself | not the charter's log: the node or skill that owns the topic | file it through `canonize` | the fact has one home (`graph-lint.py` passes) |
| frontmatter invalid | frontmatter | fix quoting, indentation, key names | `<AGENT_LINT> --lint` passes |

Three rows differ from a charter-local lessons log on purpose. A failure
mode, or a way of working that proved itself, is a fact about the subsystem,
so it lives in the node that owns the subsystem, and every agent that touches
it reads it there. An owner's rule lives in the node that owns its topic.
Writing any of them into a charter's own log makes a second home that drifts,
and is lost when a graft refreshes the charter (ADR-0013, harness memory is
not a home, makes the same point for memory files).

## 3. Make the smallest coherent edit

Edit only the section the table names, and make it read as if it had always
said that (`skills/holistic-editing/SKILL.md`). Usually one or two sections
change. Keep additions short and deduplicated against the rest of the
charter.

When the edit changes the agent's name or scope, update in the same edit
every charter that names it (boundary lines, `delegates_to`) and its rows in
`<GOLDEN>`. `--lint` catches a dangling `delegates_to`, but not a stale
boundary sentence.

**Whose file it is.** An `origin: project` charter belongs to the plant; edit
it in place. An `origin: seed` charter and `<GOLDEN>` are seed-owned: every
install fast-forwards them, and graft replaces them and keeps the old file as
a backup. An edit there is a plant customization of seed machinery. Record it
as a `deviation.*` node through `canonize` and name it a harvest candidate, so
the seed can take it up and graft does not bury it. The seed has no
plant-owned golden file yet, so a routing row for a plant's own expert has no
home that survives a graft.

Hard boundaries in a charter (manual-only invocation, security routing,
validation gates, the hard-boundary lines) are never weakened by an
evolution edit. Loosening one is its own decision, put to the owner.

Never put a secret, a credential, a host or personal data in a charter, a
trigger, a golden row or an example.

## 4. Validate, then stop

Run the check the table names, then the roster-wide gates:

```sh
python3 docs/graph/agent-lint.py --lint
python3 docs/graph/agent-lint.py --eval
python3 docs/graph/graph-lint.py
```

`--eval` reports each golden class separately. A trigger edit must leave
the `contract` class whole and must not add a confident wrong answer to the
`adversarial` class. Never widen a trigger to make a bait row pass: a bait
row exists to catch exactly that widening.

Then re-project the charter into the harness directories the plant records
(`templates/agent.template.md` says how), because a charter edited only in
the graph does not reach the next spawn.

Stop when the named deficiency is fixed. Record the edit (deficiency,
evidence, section, check result) in the delivery summary, and leave the next
deficiency for its own edit.

## Reference files

- `templates/agent.template.md` (charter sections, frontmatter, projection)
- `skills/holistic-editing/SKILL.md` (integrating the edit)
- `protocols/deliver.md` (routing-attribution assertion; misroute signals)
- `protocols/canonize.md` (where lessons land at close-out)
- `core/method/stewardship-posture.md` (§6, the operator node and the session
  record)
- `docs/decisions/adr-0013-harness-memory-is-not-a-home.md`
- `integrations/claude-code/agent-lint.py` (installed as
  `docs/graph/agent-lint.py`) and the header of `agents/_routes.golden.tsv`
  (what each golden class means)
