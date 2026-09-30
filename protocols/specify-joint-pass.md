---
name: specify-joint-pass
description: Write the spec and the plan in one joint specify-and-grill pass, held to a design latitude (creative, balanced or simple) the session classifies and records in the plan, asking the owner only in doubt. Use when a change needs both a new spec and a new plan-of-record, or when the design latitude must be classified or checked.
id: protocol.specify-joint-pass
tier: 2
kind: protocol
origin: seed
title: specify joint pass — one specify-and-grill pass, held to a design latitude classified like a tier
owns:
  - specify.joint-pass
  - specify.design-latitude
requires:
peers:
  - protocol.specify
  - protocol.grill
load_when:
  - "write the spec and the plan together, joint specify and grill pass"
  - "design latitude, creative balanced or simple, how much design freedom"
  - "out of scope under simple, the owner did not ask for it"
prevents: A design that drifts past what the owner wanted because nobody asked how much freedom it had, and specialists spawned twice over for a spec and a plan they could have written in one visit.
est_tokens: 1101
---

# Protocol: specify joint pass

Use this when a change needs a spec and a plan-of-record and neither
exists yet. `specify` and `grill` each run as a phased pass of their
own; here they run as one, and each specialist writes its spec part and
its plan part in the same spawn. Before any of it, the session
classifies how much design latitude the change has, and every later
step is held to it.

## Design latitude (`specify.design-latitude`)

| Value | Means | Held how |
|---|---|---|
| `creative` | the design may propose new structure, concepts or scope, each surfaced as a decision | the press checks each proposal is recorded as a decision the owner can refuse |
| `balanced` | new structure where the change needs it; no new concepts the goal did not ask for | the press checks every new concept traces to the goal |
| `simple` | the smallest design that meets the goal; no new gates, kinds, agents or renamed concepts; when unsure whether something is in scope, it is not | the press and every ruling refuse anything outside the adopted scope and send it to the question file |

The session classifies the latitude the way it classifies a tier: from
the request, its tone and what the work is trying to accomplish. It
states the value out loud with the reason, in step 0 below, or in
`specify`'s phase 0 when `specify` runs alone. Only when the request
leaves the value in doubt does it ask the owner, once, at the start of
the spec definition, and use the owner's own words. The value is
recorded as a row of the plan's §6 (Decisions Made) whose first cell
begins `Design latitude:`, with the session's reason or the owner's
quote as evidence, and the date.

Judgment checks the recorded value, not a tool, at three points: the
press (`grill.press`), each ruling pass (`delegation.question-file` in
`docs/graph/method/delegation-cycle-economy.md`), and every brief, which
quotes the row. Anything outside the latitude goes to the batch's
question file instead of into the build; under `simple` the ruling refuses
it, and ONLY the owner can widen the scope.

## The joint pass (`specify.joint-pass`)

The table is the spawn order (`delegation.sequencing`), as in
`specify.flow` and `grill.flow`.

| Step | Owner | Writes | Needs | Parallel with |
|---|---|---|---|---|
| 0 | session | the design-latitude classification; spec §0 to §2; plan §0, §2 to §4, §1 | — | `research-scout` for missing library pages (plan §5) |
| 1 | `product` | spec §3 | 0 | the scouts |
| 2 | `architect` | spec §4 to §8; plan §5 synthesis, §6 to §9 with effort labels, phases and the batch plan | 1, the scouts | — |
| 3 | `product` (spec §9) ∥ `tester` (spec §10 rows, testability; plan §10) ∥ `security` where the surface is sensitive (spec §5, §7; plan §11) ∥ `reliability` (plan §11) | as named | 2 | each other |
| 4 | `devils-advocate` for one-way doors and the top risk | beside the plan's §6 and §11 | 3 | — |
| 5 | session | spec §11, §12 and sign-offs; plan §12 to §15 | 4 | — |

Section ownership does not change: each section has the owner
`specify.flow` or `grill.flow` gives it. A testability failure in step 3
returns to the architect as a `protocol.recover` attempt, as it does in
`specify`. When only one document is being written, the separate phase
tables in `specify.flow` and `grill.flow` still apply. The effort labels
and phases step 2 writes are `delegation.effort-scale`
(`docs/graph/method/delegation-cycle-economy.md`).

## Neighbours

- `protocol.specify`: load when only the spec is being written, or a
  spec is being revised.
- `protocol.grill`: load when only the plan is being written or
  revised, or the plan is being pressed.
