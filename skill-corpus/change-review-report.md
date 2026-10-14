---
name: change-review-report
description: Write the self-contained report from which a reviewer who will not read the diff accepts, rejects or corrects one substantial change, with evidence behind every claim, a runnable verification that includes a step that must fail, and a verdict block, then discard it on acceptance. Invoke when a change adds a code path, a request-spanning hook, a contract or schema change, an auth behaviour change, or a runtime behaviour change.
id: skill.change-review-report
tier: 2
kind: skill
title: change-review-report, the report a reviewer decides one substantial change from without reading the diff
owns:
  - change-review-report.substantial-threshold
  - change-review-report.five-sections
  - change-review-report.verification-rules
  - change-review-report.verdict-and-discard
requires:
load_when:
  - "write a review report for this change"
  - "the reviewer will not read the diff"
  - "reviewer must accept or reject this change"
  - "review report with a verification the reviewer can run"
prevents: A substantial change is accepted by a reviewer who never read the diff, from a summary with unsourced claims and no step that must fail, and the report then lingers as a second home for the decision record's facts.
est_tokens: 3198
---

# Suggested skill: change-review-report

> Optional procedure: generate a self-contained review report that lets a
> reviewer who will not read the diff accept, reject or correct one substantial
> change. The report states the decision, the harm removed, the behaviour that
> changed, what can go wrong and how to reverse it, and a verification the
> reviewer can run, with every claim citing its evidence. It records the
> reviewer's verdict, and on acceptance its durable facts move to their
> permanent home and the report itself is discarded, unless the plant must keep
> it as review evidence. Composes `skills/adr-writer/SKILL.md` (the permanent
> record the durable facts graduate into), `protocols/canonize.md` (the
> migration on acceptance), `core/method/prose-posture.md` (how reader-directed
> prose is written) and, when the change answers security or compliance
> findings, `templates/findings-report.template.md` (the form those findings are
> rendered in) **by reference, restating none of them**. Parameterized by
> `<TARGET_LANGUAGE>`, `<REVIEWER_PROFILE>`, `<DECISION_RECORD_HOME>` and
> `<REPORT_ARCHIVE>` (where the plant keeps a report it must retain; empty when
> it keeps none).

## When to apply

A change is **substantial**, and owes a report, when it does any of:

- adds a new code path;
- adds or changes a middleware, interceptor, filter, or other
  request-spanning hook;
- changes a contract or a schema;
- changes authentication or authorization **behaviour**;
- can change runtime behaviour on deploy or under load.

Below that line (a single-key configuration edit whose whole effect is
readable in one line of diff) the report is overhead and the delivery
summary already carries it. When it is unclear which side of the line a change
sits on, write the report: an unneeded one costs a page, and a missing one
leaves a change accepted unread.

**One report per change, not per finding.** Findings that describe the same
defect from different angles (a security view and a compliance view, say)
share one report, because the reviewer is deciding on one change.

## What this is not

| artifact | reader | lifetime | home |
|---|---|---|---|
| decision record | future maintainers | **permanent** | `skills/adr-writer/SKILL.md` |
| delivery summary | the session's owner | session-scoped | `protocols/deliver.md` |
| findings report | whoever must act on a set of findings | as long as the findings are open | `templates/findings-report.template.md` |
| **change review report** | `<REVIEWER_PROFILE>` | **until the verdict**, then discarded or archived | this skill |

The delivery summary answers "what did this session do". The decision record
answers "why is the system like this". A findings report answers "what is
wrong, and how badly". The review report answers a fourth question none of
them asks: **"may this specific change be accepted, by someone who will not
read the diff?"** Writing it into the decision record makes a permanent
document out of transient review scaffolding; writing it into the delivery
summary buries a change-level decision inside a session-level narrative.

When the change answers findings, the report does not redraw them. It names
the finding ids it closes, and where the reader needs the findings themselves,
they are rendered on the findings-report form, which owns their accessible
presentation.

## The procedure

### 1. Generate it in the session that made the change

Write the report at a cycle boundary: the change is green, the increment is
committed, and the context that produced it is still loaded. A report written
later is reconstructed from the diff, which is exactly the reading it exists
to spare the reviewer. The session that made the change produces the report
and does not grade it.

### 2. Fill the five sections

Every section is mandatory. An empty one is written as an explicit "none",
never omitted.

1. **Decision, in miniature.** What was chosen; what was rejected and the
   concrete reason it lost; what the choice costs downstream. Same shape as a
   decision record's four load-bearing sections, at report length. The
   sections that survive review graduate into `<DECISION_RECORD_HOME>` later,
   so writing them in that shape now is what makes the migration mechanical
   rather than a rewrite.
2. **The harm removed, stated in terms of who is affected.** Not the class
   name of the weakness and not its severity label: who could do what to whom
   before this change, and who no longer can ("anyone who guesses a
   document's number can download another department's files", not the
   weakness's class name). A reviewer accepts a change against the harm, not
   against the taxonomy. A finding id stays for traceability, but it never
   does the work of a sentence.
3. **What changed in behaviour.** What the system now does or refuses that it
   did not before: request outcomes, stored state, emitted signals. Never a
   syntactic walk of the diff; a reviewer who wanted the diff would read the
   diff.
4. **What can go wrong, and the rollback.** The plausible failure the change
   introduces, the signal that would show it, and the reversal path. An
   unrehearsed reversal is named as unrehearsed.
5. **Verification**, by the rules of step 4.

### 3. Make every claim cite its evidence

Each statement of fact in the report points at what establishes it: the
commit that made the change, the test row that holds the behaviour (with the
RED observed before the GREEN, `protocols/verify.md`), a command and its
output, or a source quoted from a retrieved copy. A claim with nothing behind
it is labelled as inference, and a value that was not established is written
`not established`, never estimated into a number. The reviewer is trusting
the report in place of the diff, so a sentence with no evidence is a place the
diff was not read for them.

### 4. Write a verification the reviewer can run

Three properties, each load-bearing:

- **Copy-pasteable.** Every command runs as written, with no placeholder the
  reviewer must resolve and no step that begins "then check that…" without
  saying how.
- **Each step states its expected result.** A step whose output the reviewer
  cannot grade is not a verification step, it is a chore.
- **A mandatory negative test: a step that must fail.** A control nobody has
  watched refuse something has not been demonstrated to be a control. The
  report therefore carries at least one step whose *pass* condition is a
  refusal: a rejected request, a denied access, a non-zero exit, a value the
  system declines to store. A verification of only passing steps proves the
  system still works, which was never in doubt; it does not prove the change
  does anything.

Two cases the properties leave open:

- **A manual step names the thing to act on**: the command, the file, the
  button. "Start the service the usual way" is not a step, because it assumes
  the reviewer shares the author's habits.
- **A change that cannot be tested in this repository says so.** One plain
  sentence states that, and names what would have to exist for the test to be
  possible (an environment, a fixture, an external service). A test that was
  not run is never written up as if it were.

### 5. Shape the report for its reader

- **One self-contained file.** The reviewer opens one document and needs
  nothing else to decide: no link that must be followed to understand a
  claim, though links to evidence are welcome.
- **Language.** Written in `<TARGET_LANGUAGE>`, taken from the project's own
  declared deliverable language: a plant fact, declared once, never assumed
  by a procedure (`core/method/vcs-posture.md`, `vcs-posture.plant-settings`).
- **Vocabulary.** Written for `<REVIEWER_PROFILE>`, the actual human who will
  decide. Any term outside that reader's vocabulary is glossed on first use,
  in-line, once. An unglossed term is a step the reviewer will skip, and a
  skipped step is an unreviewed change wearing an approval.
- **No environment-specific literal.** No host, path, port, identifier, or
  value that a different environment would falsify. Where a value differs per
  environment, name the variable that carries it, not the value.
- **Prose.** `core/method/prose-posture.md` owns how reader-directed prose is
  written; follow it, this page does not restate it.

### 6. Record the verdict in the report

The report ends with a verdict block the reviewer fills, not the author: the
verdict (**accepted**, **rejected**, or **corrected**, with the correction
stated), the reviewer's name, the date, and which verification steps the
reviewer ran. A verdict given elsewhere (a review comment, a message) is
copied into the block with where it was given, so the report and the decision
agree. The report is a request for a decision; a session that writes its own
verdict has graded its own change.

### 7. Discard it, or keep it frozen

- **On rejection or correction**, the change changes and the report is
  regenerated from the corrected work. A report is never patched to match a
  verdict it did not earn.
- **On acceptance**, the durable facts (the decision, the rejected
  alternative, the consequences) migrate into `<DECISION_RECORD_HOME>`
  through `protocols/canonize.md`'s close-out. Then, by default, **the report
  file is deleted**. Deletion is part of acceptance, not a later tidy-up: a
  report left in the tree is a second home for facts the decision record now
  owns.
- **Kept only when the plant must retain review evidence** (an audit,
  a compliance obligation, a contract that asks for proof of review), and
  only when `<REPORT_ARCHIVE>` names where. Then the report, verdict
  included, is moved there unchanged and frozen: never edited, never cited as
  the home of a fact. It is evidence that a review happened; the decision
  record stays the home of what was decided.

## Anti-patterns

- Keeping the report in the tree as the project's record of the change, or
  archiving it when the plant has no obligation to.
- A verification section with no step that must fail, or a step with no
  stated expected result.
- A claim with no evidence behind it presented as fact, or a test that was
  not run written up as run.
- Restating the diff instead of the behaviour change.
- Redrawing findings instead of naming them and rendering them on the
  findings-report form.
- The author filling in the verdict.
- Naming a host, path, or value true only in the authoring environment.
- Writing the report in a later session, from the diff.
- Leaving a term unglossed because it is obvious to the author.

## Reference files

- `skills/adr-writer/SKILL.md` (the permanent decision record the report's
  durable facts graduate into; it owns numbering, status, and the four
  sections the report's first section borrows the shape of)
- `protocols/canonize.md` (the close-out that performs the migration on
  acceptance)
- `protocols/deliver.md` (the session-facing summary this artifact is not)
- `protocols/verify.md` (the RED-before-GREEN evidence a test-row citation
  carries)
- `templates/findings-report.template.md` (the form findings are rendered on;
  this report names the findings it closes and does not redraw them)
- `core/method/prose-posture.md` (reader-directed writing, glossing, claim
  strength; followed, never restated here)
- `core/method/vcs-posture.md` (`vcs-posture.plant-settings`: where
  `<TARGET_LANGUAGE>` is declared)
- `protocols/test-first.md` (the cycle boundary the report is written at)
