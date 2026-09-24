---
status: proposed
status_date: 2026-09-24
owner: seed steward
---

# ADR-0011: donor-identifying tokens in append-only seed records are replaced in place, under one scoped exception with one home

## Status

See frontmatter, which is the single home. Filed 2026-09-24 at plan time for
the 7.29.0 "front door" harvest, planned in
[`../plans/grill-7.29.0-front-door.md`](../plans/grill-7.29.0-front-door.md)
(§6, owner decision 3 and steward decision D2; §9 increment 8). Increment 8
lands the exception, and the status stays `proposed` until the steward
ratifies it. It supersedes no earlier ADR. The owner decision it transcribes
was given on 2026-09-24 and is not re-opened here.

## Date

2026-09-24

## Context

Earlier harvests left donor-identifying tokens in the seed. The 7.29.0 triage
found two donor-plant identifiers in nine files and a donor directory name in
two test fixtures (plan §1). The list derived for increment 8 also reaches
three records the seed treats as append-only: an earlier `CHANGELOG.md` entry,
the 7.28.0 plan, and `docs/specs/SPEC-0003-per-prompt-injection.md`, which
quotes router output carrying donor node ids (plan §9 increment 8). Harvest G1
scans only changed files, so tokens that predate a branch are never flagged
again. Leaving them means the seed does not come out of a harvest as agnostic
as it went in.

The owner chose to clean them in this harvest instead of adding an erratum
(owner decision 3). The seed's append-only convention
([`CLAUDE.md`](../../CLAUDE.md), Conventions, "Append-only artifacts") does not
allow an in-place edit of those records. Cleaning them therefore needs an
exception to an append-only rule, and the reason for that exception has to
outlast the harvest that made it. That is what an ADR is for (plan §6,
steward decision D2).

## Decision

**The seed makes one exception to its append-only convention, for
donor-identifying tokens only. The exception's scope and its four limits are
written once, in [`CLAUDE.md`](../../CLAUDE.md), Conventions, "Append-only
artifacts", and this record links that home and does not restate it.**

The tradeoff: history keeps the original text, and each edit is disclosed.
The seed gives up byte-for-byte append-only records so that the default
branch and future clones stop carrying a donor's identity.

## Consequences

- Increment 8 applies the exception to the append-only records its derived
  list hits (plan §9 increment 8, "Files touched"). Test files and fixtures
  are not append-only, so their edits are ordinary changes that keep each
  test's intent with a synthetic token.
- The convention's home gains the exception once, in increment 8. The
  restatements at `DOCUMENTATION.md:970`, `DOCUMENTATION.md:974` and
  `docs/decisions/index.md:45` keep their sentences and each gains a link to
  that home, so no restatement reads as unconditional (plan §6 row 102).
- ADR bodies are outside the exception (see its home). If the derived list
  hits a file under `docs/decisions/`, that body is left untouched. The hit
  is recorded in the plan by path and token class as the named residual
  `DONOR_TOKEN_IN_ADR_BODY`, and the steward's whole-tree G1 excepts exactly
  that path. The 7.29.0 CHANGELOG never names an excepted path.
- The original text stays at tag v7.28.0, in history, and in tags and
  Releases already published. History is not rewritten. The redaction removes
  the tokens from the default-branch view and from future clones' working
  trees, and does nothing else.
- The exception does not ship. `CLAUDE.md` is seed-side and `install.sh` does
  not place it into projects.
- Landing increment 8 ends the last-in-first-out rollback path for
  increments 1 to 7. From that commit, defects are fixed forward (plan §6
  row 103).
- Verification: increment 8's gate greps for the limits' text and must find
  one home, `CLAUDE.md`. The reviewer's word-diff against v7.28.0 must show
  only substitutions of the one fixed placeholder plus appended lines. The
  whole-tree G1 with the derived list is run by the steward locally and never
  in CI, because the list is never committed. No CI test would fail if this
  decision were silently reversed. That gap is recorded here and not closed.

## Alternatives considered

### Erratum only

Append a dated correction to each affected record and edit nothing. Append-only
stays literal, no exception or ADR is needed, and HEAD agrees with tag v7.28.0.
It was not chosen, because the owner chose to clean the records (owner
decision 3). Cleaning buys less than the first version of this option's kill
fact said (plan §7, restated row). It keeps the tokens out of the
default-branch view and future clones' working trees. History, tag v7.28.0
and published Releases still carry them. The whole-tree `git ls-files` G1
that an erratum would fail is this plan's own stricter gate (plan §8 security
posture, §9 increment 8). It is not harvest G1, which scans changed files only
(`protocols/harvest.md:335`, `:401`), so an erratum would not have failed
harvest G1. A hit in an ADR body gets a documented whole-tree G1 exception
either way.

### Redact in place with disclosure, with no stated limits

This was the first form of the redaction (plan §6 row 78). It was superseded
by the four-limit form (row 95, security S4). Without limits, an in-place
edit could reword or delete sentences, which would lose the visible record of
what changed that append-only exists to keep. Writing the limits down in one
home also stops the exception from being cited more widely than it was
written.

## Reversibility

`one-way` at increment 8's commit, and `reversible` before it, while nothing
has landed. After the commit, reverting would put donor tokens back in HEAD,
and plan §6 row 91 forbids reverting increment 8. The substitutions cannot be
undone without doing that. The exception's text could later be removed from
`CLAUDE.md` by a superseding ADR, but the records it already edited stay
edited. Because increment 8 is never reverted, landing it also closes the
last-in-first-out rollback path for increments 1 to 7.

## References

- Plan: `docs/plans/grill-7.29.0-front-door.md` §1, §6 (owner decision 3,
  rows 91, 95, 102, 103), §7 (erratum-only, restated), §9 increment 8
- Convention home: [`CLAUDE.md`](../../CLAUDE.md), Conventions, "Append-only
  artifacts"
- Spec: `docs/specs/SPEC-0003-per-prompt-injection.md` (a redacted record;
  its changelog line discloses the redaction)
- Harvest gates: `protocols/harvest.md` (G1)
