# Suggested skill: fix-review-packet

> Optional procedure — a substantial security or compliance fix ships with a
> **throwaway** review file that lets a non-specialist reviewer accept or
> reject it without reading the diff. Not a core skill; instantiate into
> `docs/graph/skills/<name>.md` (its home, projected into the harness dirs the
> plant uses) from `templates/skill.template.md` if selected. **Composes**
> `skills/adr-writer/SKILL.md` (the permanent record the packet's durable facts
> graduate into), `protocols/canonize.md` (the migration on acceptance), and
> `core/method/prose-posture.md` (how reader-directed prose is written) **by
> reference, restating none of them**. What it adds is a third artifact class
> the seed does not own: fix-facing, reviewer-directed, and deliberately
> temporary. Parameterized by `<TARGET_LANGUAGE>`, `<REVIEWER_PROFILE>`,
> `<DECISION_RECORD_HOME>`.

## When to apply

A fix is **substantial** — and owes a packet — when it does any of:

- adds a new code path;
- adds or changes a middleware, interceptor, filter, or other
  request-spanning hook;
- changes a contract or a schema;
- changes authentication or authorization **behaviour**;
- can change runtime behaviour on deploy or under load.

Below that line — a single-key configuration edit whose whole effect is
readable in one line of diff — the packet is overhead and the delivery
summary already carries it.

## What this is not (three artifacts, three lifetimes)

| artifact | reader | lifetime | home |
|---|---|---|---|
| decision record | future maintainers | **permanent** | `skills/adr-writer/SKILL.md` |
| delivery summary | the session's owner | session-scoped | `protocols/deliver.md` |
| **fix review packet** | `<REVIEWER_PROFILE>` | **deleted on acceptance** | this skill |

The delivery summary answers "what did this session do". The decision record
answers "why is the system like this". The packet answers a third question
neither of them asks: **"may this specific fix be accepted, by someone who
will not read the diff?"** Writing the packet into the decision record makes a
permanent document out of transient review scaffolding; writing it into the
delivery summary buries a fix-level decision inside a session-level narrative.

## The packet's sections

Every section is mandatory. An empty one is written as an explicit "none",
never omitted.

1. **Decision, in miniature.** What was chosen; what was rejected and the
   concrete reason it lost; what the choice costs downstream. Same shape as a
   decision record's four load-bearing sections, at packet length — the
   sections that survive review graduate into `<DECISION_RECORD_HOME>` later,
   so writing them in that shape now is what makes the migration mechanical
   rather than a rewrite.
2. **The harm removed, stated in terms of who is affected.** Not the class
   name of the weakness and not its severity label: who could do what to whom
   before this change, and who no longer can. A reviewer accepts a fix against
   the harm, not against the taxonomy.
3. **What changed in behaviour.** What the system now does or refuses that it
   did not before — request outcomes, stored state, emitted signals. Never a
   syntactic walk of the diff; a reviewer who wanted the diff would read the
   diff.
4. **What can go wrong, and the rollback.** The plausible failure the change
   introduces, the signal that would show it, and the reversal path. An
   unrehearsed reversal is named as unrehearsed.
5. **Verification.** See below.

## The verification section

Three properties, each load-bearing:

- **Copy-pasteable.** Every command runs as written, with no placeholder the
  reviewer must resolve and no step that begins "then check that…" without
  saying how.
- **Each step states its expected result.** A step whose output the reviewer
  cannot grade is not a verification step, it is a chore.
- **A mandatory negative test — a step that must fail.** A control nobody has
  watched refuse something has not been demonstrated to be a control. The
  packet therefore carries at least one step whose *pass* condition is a
  refusal: a rejected request, a denied access, a non-zero exit, a value the
  system declines to store. A verification section of only passing steps
  proves the system still works, which was never in doubt; it does not prove
  the fix does anything.

## Writing rules

- **Language.** The packet is written in `<TARGET_LANGUAGE>`, taken from the
  project's own declared deliverable language — a plant fact, declared once,
  never assumed by a procedure (`core/method/vcs-posture.md`,
  `vcs-posture.plant-settings`).
- **Vocabulary.** Written for `<REVIEWER_PROFILE>` — the actual human who will
  accept or reject. Any term outside that reader's vocabulary is glossed on
  first use, in-line, once. The gloss is not a courtesy: an unglossed term is
  a step the reviewer will skip, and a skipped step is an unreviewed fix
  wearing an approval.
- **No environment-specific literal.** No host, path, port, identifier, or
  value that a different environment would falsify. A literal that is true in
  exactly one place turns the packet into a trap for whoever reads it in the
  second place.
- **Prose.** `core/method/prose-posture.md` owns how reader-directed prose is
  written — claim classes, structure carrying emphasis, when a sentence is too
  strong for its evidence. Follow it; this page does not restate it.

## Lifecycle

1. **Produced by the same session that did the work**, at a cycle boundary —
   the fix is green, the increment is committed, the context that produced it
   is still loaded. A packet written later is reconstructed from the diff,
   which is exactly the reading the packet exists to spare the reviewer.
2. **A human accepts, rejects, or corrects it.** The packet is a request for a
   decision; the session does not grade its own fix.
3. **On acceptance**, the durable facts — the decision, the rejected
   alternative, the consequences — migrate into `<DECISION_RECORD_HOME>`
   through `protocols/canonize.md`'s close-out, and **the packet file is
   deleted**. Deletion is part of acceptance, not a later tidy-up: a packet
   left on disk is a second home for a fact the decision record now owns.
4. **On rejection or correction**, the fix changes and the packet is
   regenerated from the corrected work. A packet is never patched to match a
   verdict it did not earn.

## Anti-patterns

- Keeping the packet as permanent documentation, or committing it as the
  project's record of the fix.
- A verification section with no step that must fail.
- A verification step with no stated expected result.
- Restating the diff instead of the behaviour change.
- Naming a host, path, or value true only in the authoring environment.
- Writing the packet in a later session, from the diff.
- Leaving a term unglossed because it is obvious to the author.
- Folding the packet into the delivery summary, or into the decision record,
  instead of letting each carry its own lifetime.

## Reference files

- `skills/adr-writer/SKILL.md` (the permanent decision record the packet's
  durable facts graduate into — owns numbering, status, and the four sections
  the packet's first section borrows the shape of)
- `protocols/canonize.md` (the close-out that performs the migration on
  acceptance)
- `protocols/deliver.md` (the session-facing summary this artifact is not)
- `core/method/prose-posture.md` (reader-directed writing, glossing, claim
  strength — followed, never restated here)
- `core/method/vcs-posture.md` (`vcs-posture.plant-settings` — where
  `<TARGET_LANGUAGE>` is declared)
- `protocols/test-first.md` (the cycle boundary the packet is written at)
