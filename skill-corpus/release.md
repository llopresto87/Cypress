# Suggested skill: release

> Optional procedure — **a template**. A numbered, resumable acceptance round
> across a multi-component delivery: re-measure after the baseline moves,
> re-issue the formal acceptance package from the measured values, have an
> independent reader re-check every statement, close with a report. The round
> **never signs, never declares conformity, and never authorises a release.**
> Not a core skill; instantiate into `docs/graph/skills/<name>.md` (its home,
> projected into the harness dirs the plant uses) from
> `templates/skill.template.md` if selected. **Composes**
> `core/method/release-posture.md` (what the round measures against) and
> `agents/12-devils-advocate.md` (phase 6's reader) **by reference and restates
> neither**. What it adds is the numbered, resumable round itself: the
> measure-then-generate ordering, the three-state gate, and the three-state
> verdict.

**Instantiate by supplying:** `<COMPONENTS>` and each one's base reference,
`<BASELINE_ARTIFACT>`, `<PACKAGE_TEMPLATES>` and their placeholder convention,
`<ACCEPTANCE_ENVIRONMENT>`, `<GATE_SCRIPT>` and its three outcomes,
`<RECEIVING_AUTHORITY>`, the two identifier schemes (jointly agreed, which
stays; internal, which is stripped), and `<PACKAGE_LANGUAGE>`.

**Language.** The round's own working record — the baseline, the gate output,
the report — is written in **English by default**. `<PACKAGE_LANGUAGE>` is a
separate parameter and governs only the deliverable package of phase 5, because
the language a receiving party accepts a document in is a property of the
agreement, not of the procedure: a round run in one language may have to hand
over a package in another. Where a project declares a deliverable language of
its own, that declaration supplies `<PACKAGE_LANGUAGE>` and this page does not
second-guess it. Nothing in the procedure depends on the language of either —
the phases, the gate's three outcomes, and the verdict's three states are the
same in any language, and a term that has no clean equivalent is carried in the
original with a gloss on first use rather than translated into a near-miss.

## When to apply

- A delivery spanning several independently versioned components must be
  handed to a receiving party with a formal acceptance package.
- The baseline has moved since the last package was issued, so every figure in
  it is now a claim about a version that no longer ships.
- A previous round was blocked or partially completed and must resume without
  re-running what already held. Rounds are **numbered**; a round is resumable
  by number, and its phases are re-enterable.

## Phase 1 — Preflight

**Gate: every component in scope is clean, remote-aligned, and on a recorded
reference; the auxiliary toolchain is confirmed present.**

- Each of `<COMPONENTS>` is in a known-clean, remote-aligned state on an
  **explicit, decided-and-recorded** reference.
- **Heterogeneous components may not share one integration branch.** They
  release on different cadences; a single shared branch name resolves to
  different content per component and hides that it did.
- **The per-component choice of reference is itself a decision that determines
  what ships**, so it is written down rather than silently inferred from
  whatever is checked out.
- **The auxiliary toolchain the later phases need is confirmed present now** —
  document rendering, checksum tooling, the scanner, the gate interpreter.
  Discovering a missing tool after measurement, testing, and scanning have
  already run is the specific failure this step exists to prevent: the cost is
  not the install, it is re-running everything upstream of it.

## Phase 2 — Lane preparation

**Gate: a clean release lane per component, secrets-scanned before use.**

- Create the round's release lane per component, named for the round.
- **Refuse to proceed over an existing unsecured lane.** A lane left from a
  previous round carries that round's state; reusing it silently mixes two
  baselines.
- **Run a secrets scan before anything else touches the lane**, with the
  null-result control `protocols/verify.md` requires of a clean scan.
  `core/method/secrets-posture.md` owns what a hit means and the order of
  remediation.

## Phase 3 — Baseline measurement

**Gate: one measured-facts record across the scope, provenance-consistent and
security-scanned.**

Build **one** `<BASELINE_ARTIFACT>` — versions, identifiers, checksums —
covering the whole scope. One record, not one per component and not one per
document.

**The release's own immutable identifier is a mandatory input to this phase,
never resolved implicitly.** Resolving to "the latest built" instead of "the
named release" silently measures the wrong artifact and produces a baseline
that is internally consistent and about the wrong thing.
`core/method/release-posture.md` (`release-posture.artifact-identity`) owns
why identity is immutable; this phase only insists it be supplied rather than
inferred.

## Phase 4 — Acceptance verification

**Gate: none — this phase is deliberately not a hard gate.**

- An item **not yet measurable** is marked with its own explicit **"not
  measured"** state — neither pass nor fail — and the round proceeds. Blocking
  the round on an unmeasurable item converts a known gap into a stall and
  tempts someone to record a pass.
- **Whatever this phase measures is written into the same
  `<BASELINE_ARTIFACT>` from phase 3**, never into a separate later document.
- **This ordering is load-bearing.** Running acceptance testing *after*
  document generation produces documents whose figures are never updated,
  because nothing routes the test facts back into them. Measure, then
  generate — in that order, every round.

`<ACCEPTANCE_ENVIRONMENT>` is named in the instantiated page, along with what
it does and does not reproduce.

## Phase 5 — Package regeneration

**Gate: no placeholder token survives into any rendered output, verified
independently of the generator.**

- Regenerate **every** deliverable document from `<PACKAGE_TEMPLATES>` in
  `<PACKAGE_LANGUAGE>`, using
  **only** the measured baseline's values.
- **By substitution, never by hand-editing.** A hand-edited figure is a figure
  with no provenance, and it is always the one that turns out to be stale.
- Verify the rendered output **independently** — a separate check that no
  placeholder token remains, not the generator reporting on itself.
- A duplicated convenience copy for recipients is **explicitly marked
  non-authoritative** in the copy itself, so that a stale duplicate cannot be
  mistaken for the record.

## Phase 6 — Independent adversarial re-check

**Gate: every statement re-checked against raw sources by a reader who did not
author the documents.**

This phase is `agents/12-devils-advocate.md`, used as-is. That agent already
owns the seed's independent-reader doctrine — the primary-source rule, the
ranked attack by claim load, the steelman-then-attack method, the closed
verdict vocabulary whose permanent ceiling is "could-not-refute", and the
requirement to name its own blind spot. **This page composes it by reference
and invents no parallel doctrine for it.** Read that file before running the
phase.

Two round-specific additions, which are this page's own:

- The reader **opens the raw underlying sources directly** — the measured
  baseline, the component references, the scan output — never a summary handed
  to them by the author of the documents.
- **Findings persist and are tracked open/closed across rounds**, by round
  number, rather than being re-discovered each time. A finding that was open
  in the previous round and is not addressed in this one is carried forward as
  open, not silently dropped because nobody re-found it.

## Phase 7 — Close-out and report

**Gate: `<GATE_SCRIPT>` has run, its output is filed, and the report exists.**

**The report is written every time — including when the round is blocked.**
Its job is to state the conclusion, not merely to gate. A blocked round with
no report leaves the receiving party with silence, which they will read as
either progress or failure, and both readings are guesses.

**The readiness evaluation is mechanical, not prose.** `<GATE_SCRIPT>`
evaluates the baseline and returns **exactly one of three outcomes**:

| outcome | meaning |
|---|---|
| complete | every required item is measured and passing |
| incomplete | named reasons, item by item |
| **not adjudicable** | the round cannot even be judged — e.g. a baseline that is missing or unreadable |

The third state is the one most gates lack. Without it, an unreadable baseline
is reported as "incomplete", which says the round was judged and fell short —
a different and false statement. `<GATE_SCRIPT>`'s **own output is filed as
the evidence the report's verdict is read from**, so the verdict is traceable
to a machine result rather than to the author's reading of one.

**The round's verdict is likewise exactly one of three states:** ready · ready
with reservations · not ready. An item marked "not measured" in phase 4 counts
as **neither compliant nor non-compliant**, and the verdict says so rather
than resolving the ambiguity in either direction.

**The process never signs and never authorises release.** That authority is a
**named, dated human decision on the receiving party's side**
(`<RECEIVING_AUTHORITY>`), recorded outside this process's output. A round
that signs has quietly moved a decision from the party accountable for it to
the party producing the evidence for it.

**Identifier hygiene at the handover:** internal procedure-reference numbers
are stripped from anything handed to the receiving party; identifiers **jointly
agreed with them** stay. The instantiated page names both schemes explicitly,
because the distinction is not inferable from the identifiers' shapes.

## Anti-patterns

- Generating the package first and testing afterwards — the figures are then
  never updated.
- Letting acceptance verification block the round instead of recording "not
  measured".
- Hand-editing one figure in a rendered document rather than re-substituting.
- Sharing one integration branch across heterogeneous components.
- Letting the baseline resolve to "the latest built" instead of the named
  release identifier.
- Handing the independent reader a summary instead of the raw sources.
- Re-discovering findings each round instead of carrying them by number.
- A prose readiness judgement in place of a gate, or a gate with only two
  outcomes.
- Skipping the report because the round was blocked.
- Signing, declaring conformity, or authorising the release from inside the
  round.
- Confirming the auxiliary toolchain after measurement has already run.
- Shipping internal procedure-reference numbers to the receiving party.

## Reference files

- `core/method/release-posture.md` (artifact identity, readiness, and rollout
  ordering — what the round measures against)
- `agents/12-devils-advocate.md` (phase 6 in full: primary-source rule, ranked
  attack, closed verdict vocabulary, blind-spot declaration — composed, never
  restated)
- `core/method/secrets-posture.md` (phase 2's scan and what a hit obliges)
- `protocols/verify.md` (gate states, and the null-result control a clean scan
  owes)
- `core/method/incident-posture.md` (a carried-forward finding is a named
  residual with an owner and a trigger)
- `protocols/canonize.md` (what the round's durable facts owe the graph at
  close-out)
