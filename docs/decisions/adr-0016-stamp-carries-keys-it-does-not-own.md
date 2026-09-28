---
status: proposed
status_date: 2026-09-28
owner: seed steward
---

# ADR-0016: the seed stamp is an open record: the installer carries forward every key it does not own

## Status

See frontmatter, which is the single home. Filed 2026-09-28 for 7.32.0 by the
round's joint specify and grill pass, planned in
[`../plans/grill-7.32.0-harvest.md`](../plans/grill-7.32.0-harvest.md). The
owner ratified the round's scope; this record stays `proposed` until the
increments it names land. It supersedes no earlier ADR.

## Date

2026-09-28

## Context

`install.sh`'s `write_seed_stamp` reads five known fields from
`.cypress/seed.json` and writes a fixed set of keys. Its own comment says a run
"MERGES into it and never narrows it", but any key the installer does not name
is dropped. A graft that recorded its provenance in the stamp lost it at the
next re-install, with no warning. The code and its comment disagreed, and the
owner chose the comment (decision 2 of the plan).

## Decision

The installer owns its keys and their rules. Every other key in the stamp is
carried forward unchanged, in its original order, after the installer's own
keys. A stamp that does not parse as one JSON object is moved aside to a
backup before the installer writes a stamp of its own keys, and one warning
says so.

## Consequences

- A tool or a steward can annotate the stamp, and the annotation survives
  every later install.
- A key written by hand also survives for ever. The installer validates only
  the keys it owns, as it does today for `legal_corpus`.
- SPEC-0001 gains `UNKNOWN_STAMP_KEYS_SURVIVE` and the failure
  `STAMP_NOT_AN_OBJECT`, pending until their RED lands.
- The stamp's parse moves to `python3`, which the installer already requires.
- Test that fails if this is reversed: the unknown-keys case of
  `tests/test-plant-state.sh` (plan increments 15 and 38).

## Alternatives considered

- **Strict schema: correct the comment and keep dropping unknown keys.**
  Rejected by the owner. Any tool that wants to annotate a plant would need a
  file of its own beside the stamp.
- **Refuse to install over a stamp that is not a JSON object.** Rejected: a
  hand-broken stamp would block every install, including the one that repairs
  it. Moving it aside keeps its bytes and lets the install proceed.

## Reversibility

`reversible now → expensive after plants store keys in the stamp`: once a tool
relies on a carried key, dropping carried keys loses that tool's record.

## References

- Spec: SPEC-0001, pending block of §4
- Grill: plan §6 decision 2, §9 increments 15 and 38
