---
status: accepted
status_date: 2026-11-03
owner: seed steward
---

# ADR-0032: each close-out fact has one home; the session record keeps only what no other file holds

## Status

See frontmatter, which is the single home. It amends
[ADR-0013](adr-0013-harness-memory-is-not-a-home.md) in one place: the record's third kind of
learning, resume state. The owner decided on 2026-11-03 to keep the session
record and improve the close-out so that each fact is written once, after asking
first for an account of why the mechanism exists. ADR-0013's other decisions
stand: the record lives in the plant, the orchestrating session writes it at the
moment it learns, canonize files it, and harness memory holds at most a pointer.
[ADR-0018](adr-0018-code-fact-freshness-anchor.md) stands: the code-anchor line stays in
the record's "Canonize status".

## Date

2026-11-03

## Context

ADR-0013 answered three gaps: a learning had nowhere to live between the moment
it was learned and the close-out, so a session that ended early lost it; harness
memory went stale unseen; and canonize had no session-level input. It gave the
record three kinds of learning: owner rules, corrected assumptions, and resume
state.

At delivery the seed then wrote one account in up to five places. `protocol.deliver`
told the session to state the summary in the chat and append the same content
to the plant `changelog.md` and to `grill.md` §15; the record's "Open threads"
restated where the work stood; the commit message and the handbacks carried
their own parts. Progress and the next action already had a home that every
resuming session reads: `grill.md` §15 logs each increment as it lands and §14
names the next action (`delegation-sequencing`, `delegation.tracing`).

The 8.3.0 trajectory audit found that the parts no other file held, owner rules
and corrected assumptions, were the ones later sessions and the librarian used,
while the resume-state blocks repeated the plan.

## Decision

1. The delivery is written once, as the plant `changelog.md` entry. `grill.md`
   §15 gets one line pointing at that entry, and the chat gets the summary with
   the same pointer (`protocol.deliver`, full form).
2. The record's "Open threads" becomes "Paused state", written only for a live
   operation stopped mid-flight: what is applied where, the rollback anchors and
   how long each survives, the blocker's next diagnostics, the gates still to
   run. Routine progress and the next action stay in `grill.md` §15/§14.
3. A session resumes from `grill.md` §14 and the newest §15 entries, then the
   newest record's "Paused state" block and its unfiled items (kernel §3.2,
   `stewardship-posture.session-record`).
4. The record is still opened for every T2/T3 unit of work, so canonize's
   finding "no session record" keeps its signal.

## Consequences

- A close-out writes the delivery once instead of three times, and a record
  holds owner rules, corrected assumptions, paused state, harness migration and
  canonize status: the parts nothing else holds.
- The mid-plan loss ADR-0013 guarded against stays covered, because §15 is
  written at every commit and §14 before every pause, which the rule now names.
- Records written before 8.3.0 keep their "Open threads" blocks as written; a
  session reads them as paused state.
- A Stop hook that greps a delivery's attribution lines reads the changelog
  entry, its one home.

## Alternatives considered

- **Retire the record.** Owner rules would return to harness memory or be taught
  again, the failure ADR-0013 was written for.
- **Create the record only on its first item.** Fewer empty files, but canonize
  would lose the "no session record" signal that a write-at-the-moment rule was
  skipped.
- **Keep resume state in both places.** Two homes drift; the audit found them
  restating each other.

## Reversibility

Two-way. Restoring "Open threads" and the triple delivery write is a text change
in `protocol.deliver`, `method.stewardship-posture` and the record template.

## References

- [ADR-0013](adr-0013-harness-memory-is-not-a-home.md), [ADR-0018](adr-0018-code-fact-freshness-anchor.md)
- `core/method/stewardship-posture.md` (`stewardship-posture.session-record`)
- `protocols/deliver.md`, `protocols/canonize.md` (`canonize.session-record`)
- SPEC-0005 §6 "Session record", §12 (version 0.17)
