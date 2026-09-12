# ADR-0006: T2 gains a contained lane — a small change is authorized by a test and a why, not a spec

## Status

`accepted` — shipped as **7.14.0** (2026-09-13). Amends the tier edges set in
`core/method/tiers.md` (`method.tiers`) and the §3.1 spec-rule anchor in the
kernel. It does not supersede [ADR-0004](adr-0004-pure-graph-architecture.md);
the graph architecture is unchanged.

## Date

2026-09-13

## Context

Through 7.13 the tier edges left a gap that real maintenance falls into
constantly. T1 was defined by touching **no** behavior, contract, or spec
surface. T2 required that an **active spec contract already authorize** the
change — "no active spec contract covering the change means it is T3, however
small it looks". Everything else was T3: brainstorm* → specify → grill →
test-first → verify → canonize → deliver.

A two-line defect fix in code no spec covers matches neither T1 nor T2. It
touches behavior, so T1 is closed by its own hard edge; no spec covers it, so
T2 is closed by its own. It therefore bought a `specify` pass and a `grill`
pass to authorize two lines — the most common shape of maintenance work paying
the most expensive path in the system.

The cost is not primarily wall-clock. A process that is disproportionate often
enough stops being believed, and the failure mode is not that people run the
funnel slowly — it is that they quietly reclassify the change as T1, or skip
the tiers entirely. The edge that was written to prevent under-classification
was producing it.

"Do nothing" was not viable for the same reason: the gap is in the most
frequent case, not a rare one.

## Decision

**T2 becomes a *contained change* with two entry lanes.**

- **Covered lane** — unchanged: an active spec contract and plan line already
  authorize the work.
- **Contained lane** — new: no spec owns the surface, and the proportional
  authorization is **the failing test that pins the behavior** plus **a
  recorded why** at close-out, instead of a spec document.

The lane opens only when **every** condition holds: one surface (no contract,
public interface, persisted format, or schema); no new dependency; reversible
by revert (no migration, no one-way door, no auth/security/concurrency change);
no active spec owns the surface; and the intent fits in a decision note. Any
doubt about any one of them is T3 — the edge is unanimous, and it escalates
mid-task the moment the work outgrows it.

The lane trades away `specify`, the `grill` pass, and the refutation spawn. It
trades away nothing else: the RED test, the independent reviewer audit, the
gates the blast radius earns, and the close-out record all stand. Gate depth
follows blast radius, never the lane (`protocol.verify`).

The **why-record** is what the lane owes in place of the spec, and
`protocol.canonize` owns writing it (`canonize.why-record`): one short ADR when
a real choice was made among options, otherwise one `changelog.md` line
carrying defect → cause → fix → pinning test. One entry, never both, and never
a spec — a small change that needs a spec to be explicable was misclassified,
and the honest close-out says so rather than manufacturing the spec after the
fact.

## Consequences

- The kernel's §3.1 spec-rule anchor carries an explicit exception for the
  contained lane. Without it the seed would assert a rule its own tier table
  contradicts, which is worse than either rule alone.
- `protocol.canonize`'s completeness claim grows from four items to five; a
  contained-lane task delivered with no why-record is a fifth leak class beside
  the uncaptured fact, tool, status, and deviation.
- Delivery metrics name the lane, not just the tier, so post-hoc review can ask
  whether contained-lane changes are staying inside their conditions.
- Plants grafting 7.14.0 inherit a *wider* T2. Existing T0–T3 records keep their
  meaning — no tier was renumbered, which is why the lane was added inside T2
  rather than inserted as a fifth tier between T1 and T2.
- The lane is the seed's most abusable surface: it is the one place where a
  behavior change proceeds without a spec. `tests/test-tier-lanes.sh` pins both
  halves — that the lane exists with one home and every routing surface points
  at it, and that it never acquired an exit from the test, the review, the
  gates, or the record.

## Alternatives considered

- **A fifth tier between T1 and T2.** Conceptually the cleanest fit: the new
  work genuinely sits between them in cost. Rejected because inserting it
  renumbers the current T2 and T3, and every `Tier: T2` already written in a
  plant's `grill.md` §15 and delivery records would silently change meaning.
  Corrupting the historical record to tidy the taxonomy is a bad trade.
- **Grade the T3 funnel instead, leaving the edges alone.** A small T3 would
  skip brainstorm, the refutation spawn, and the architect pass. Rejected as
  insufficient: every small fix would still pay a `specify` pass and a full
  grill entry, which is most of the cost being complained about. It remains
  available as a later, independent change.
- **Let the contained lane amend one contract into the nearest existing spec.**
  Keeps §3.1 absolute. Rejected because the common case has no nearby spec to
  amend, and the near cases invite attaching a contract to a spec that does not
  actually own the surface — which corrupts the spec index to protect a rule's
  wording.
- **Let the session author the fix in-session, extending the T1 exception.**
  Cheapest possible path. Rejected: it puts authoring back in the orchestrator's
  context, which kernel §1 exists to prevent, and the saving is one spawn.

## Reversibility

`reversible` — narrowing the lane, or removing it, is an edit to
`method.tiers` plus the surfaces that point at it, and no artifact shape depends
on it. The one cost that grows over time is *judgment* drift: the longer plants
run with the lane, the more real changes exist that were authorized by a test
and a why rather than a spec, and re-tightening the edge would leave those
changes retroactively unauthorized. Record that as `reversible now → expensive
once plants carry a body of contained-lane work`.

## References

- Node: `core/method/tiers.md` (`tiers.contained-lane`)
- Node: `protocols/canonize.md` (`canonize.why-record`)
- Kernel: `core/AGENTS.md` §0, §3.1, §4
- Gate: `tests/test-tier-lanes.sh`
- CHANGELOG: 7.14.0
