# ADR-0003: Enforcement layering, honestly labelled (tool-grant hard; caps soft; deliver-time detective)

## Status

`accepted` — implemented and verified 2026-07-13 (plan §9, P2). The optional
top-session `Stop` hook is **deliberately unwired** (green-lie discipline);
tracked as a deferred warn→block follow-up.

> This ADR is the standalone promotion of **ADR-C**, decided inline at
> `../plans/agent-routing-and-delegation.md` §3. The plan's §3 body remains the
> faithful source; this file restates it and links back. Do not re-decide here.

## Date

2026-07-13

## Context

Enforcement in the seed is prose, and the one hook (`route-hook.py`) fires only
on the top-session `UserPromptSubmit` — it cannot reach subagents, which is
exactly where routing and handback happen (plan §1, RC5). This is the
"dormant-but-enabled" trap: a control that *looks* enforced but isn't. Shipping
`max_spawn_depth: 1` as if the Claude Code harness clamped it would repeat that
trap, because the current `Task` tool does not read these fields.

## Decision

State the *effective* enforcement of each control, and never let a config field
imply enforcement the harness does not provide:

- **Hard (harness-enforced today):** which agents have `Task` in `tools`. Leaf
  agents lack it → they cannot spawn → recursion depth is bounded by the chain
  of Task-holders, which we keep short by granting `Task` to only 5 agents.
- **Soft (contract-enforced):** `can_delegate`, `max_spawn_depth`,
  `delegates_to`. The current `Task` tool does **not** read these fields or
  enforce a numeric depth / allowlist. They are enforced by `agent-lint.py
  --lint` (static), the agent prose, and the brief templates.
- **Detective (post-hoc):** the deliver-time routing-attribution assertion —
  every unit of work must carry a `produced_by` specialist (from its handback
  payload); missing `produced_by` → **BLOCK** (fail-closed); out-of-domain
  authoring or an un-rationalised generic-role override of a HIGH route → FLAG.
  It runs in the **top session** at `deliver`, the one enforcement point that
  does not hit the subagent-hook limitation, so it *can* be wired to a `Stop`
  hook — rolled out warn→block, and **not wired yet** (land the checked thing
  before the gate; kernel §3.5).

## Consequences

- `agent-lint.py --lint` asserts `can_delegate == (Task ∈ tools)` exactly, so a
  soft field can never silently drift from the hard reality.
- `deliver.md` gained the fail-closed `produced_by` assertion (P2); the brief
  templates and all 13 agents gained the handback block.
- The `Stop` hook remains **unwired on purpose** — wiring it before attributions
  reliably exist would be a green lie. Promote to warn, then block, once the
  handback payloads are routinely present.
- **Known limitation (carried into plan §7 risks):** a Task-holding subagent
  could in principle spawn outside its `delegates_to` allowlist, because the
  harness won't block it. Mitigation: keep the delegating set tiny (5) and
  allowlists leaf-only, and rely on the detective assertion. Promote the soft
  caps to hard if/when a delegation wrapper or a subagent-reaching PreToolUse
  hook exists.

## Alternatives considered

- **Claim the numeric caps are hard-enforced.** — rejected: it would mislead
  operators exactly as dormant telemetry plugins do — the precise RC5 trap this
  ADR exists to avoid.

## Reversibility

`reversible` — the labelling and the detective assertion are additive; removing
them restores prose-only enforcement.

## References

- Plan (source of the decision): `../plans/agent-routing-and-delegation.md`
  §3 ADR-C, §4.5 (deliver-time assertion), §6 P2, §7 (dormant-but-enabled +
  allowlist-escape risks), §8, §9.
- Sibling ADRs: `adr-0001-mechanical-agent-router.md`,
  `adr-0002-bounded-delegation-hybrid.md`.
- Catalog: `index.md`.
- Enforcement surfaces: `.protocols/deliver.md`,
  `templates/prompts/handback-payload.md`, `agent-lint.py --lint`.
