# ADR-0003: Enforcement layering, honestly labelled (tool-grant hard; caps soft; deliver-time detective)

## Status

`accepted` — implemented and verified 2026-07-13 (plan §9, P2), **amended
2026-09-14** (see §Amendment: a fourth label, `judgment`, and the fact that a
protocol gate is almost never `hard`). The optional top-session `Stop` hook is
**deliberately unwired** (green-lie discipline); tracked as a deferred
warn→block follow-up.

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

## Amendment — 2026-09-14: a fourth honest label, `judgment`

The 7.16.0 lifecycle-protocol rework gave `graft`, `grow` and `harvest` a single
gate table apiece, each row declaring its enforcement class in this ADR's
vocabulary. 53 rows in, two things were true that this ADR had not said.

**A protocol gate is almost never `hard`.** Hard means the *harness* makes the
wrong thing impossible — a leaf agent with no `Task` tool cannot spawn, whatever
anyone writes. No harness prevents a steward applying an upgrade, delivering a
growth, or committing a harvest. `protocols/graft.md` reached this conclusion on
its own and states it under its table; `protocols/harvest.md` initially defined
`hard` as *"a tool refuses"* and labelled its linter rows `hard`, which inverts
this ADR: §Decision names `agent-lint.py --lint` as a **soft** enforcer. A
linter that a person may choose not to run, or may run and override, is
contract-enforced. The definitions now agree across the three files, and they
agree with this ADR: **hard = the harness refuses; soft = a contract or a tool
refuses; detective = caught after the fact.**

**Some gates no tool can check at all.** Faithful import — whether an imported
artifact kept the whole of its donor's discipline — is read by a person, and
7.15.0 recorded five defects passing it. Minimum-sufficiency is weighed against
`method.engineering-posture` by a reviewer. Labelling these `soft` would claim a
contract enforces them, and none does.

So: **`judgment` — no mechanical check is possible; a named human or agent
decides.** A `judgment` row must name its judge, and naming it is the whole
point. This is not a weakening of the honesty layering, it is the layering
applied to its own blind spot: three labels for enforced things and silence
about the unenforced ones was itself a config field implying enforcement nobody
provides. `tests/seed-lint.py`'s `check_gate_single_home()` holds every row in
`LIFECYCLE_NODES` to one of the four and rejects a blank.

The original three-class decision above is unchanged and still governs the
delegation controls it was written for.

## Amendment — 2026-09-24: the size of the delegating set is read from the lint

§Decision's first bullet and §Consequences' known limitation give the size of
the delegating set as a fixed number. The roster has grown since, as
ADR-0002's 2026-07-23 amendment records, so that number no longer matches the
roster. This amendment corrects the count and nothing else, and it prints no
new number, because a number written here would go stale the same way. The
current holders are the agents whose frontmatter sets `can_delegate: true`,
and `integrations/claude-code/agent-lint.py --lint` holds that set equal to
the agents whose `tools:` line carries the grant §Decision names. The classes,
the decision and the rest of this body are unchanged.

## Amendment — 2026-09-24: hooks inside subagents, and the spawn tool's two names

§Context says the one hook "cannot reach subagents". That holds for the route
hook's top-session firing, not for the seed's hooks in general: on Claude Code,
tool events fire inside a subagent, so the seed's `PreToolUse` guard
(`bound-hook.py`) runs on a subagent's Bash calls. §Consequences names "a
subagent-reaching PreToolUse hook" as a precondition still to come; the host
already provides that mechanism, and the hook input names the subagent. The
caps stay soft because the seed wires no hook on the spawn tool that reads
`delegates_to`, not because the host cannot run one; promoting them is a
separate decision. The spawn tool's canonical name is `Agent`, with `Task` an
accepted alias, and in a subagent definition the host ignores a parenthesized
type list. So §Decision's hard class reads as "the spawn tool, under either
name, absent from an explicit `tools:` line" (an omitted line inherits every
tool), and the §Consequences invariant reads as `can_delegate == (spawn tool ∈
tools)` under either name, which is how both lints now read it. The mechanism
is in `core/method/delegation.md` (§"Delegation is bounded" and §"Every brief
carries the graph discipline"); upstream sources, retrieved 2026-09-24:
<https://code.claude.com/docs/en/hooks> and
<https://code.claude.com/docs/en/sub-agents>. The classes and the decision are
unchanged.

## References

- Plan (source of the decision): `../plans/agent-routing-and-delegation.md`
  §3 ADR-C, §4.5 (deliver-time assertion), §6 P2, §7 (dormant-but-enabled +
  allowlist-escape risks), §8, §9.
- Sibling ADRs: `adr-0001-mechanical-agent-router.md`,
  `adr-0002-bounded-delegation-hybrid.md`.
- Catalog: `index.md`.
- Enforcement surfaces: `.protocols/deliver.md`,
  `templates/prompts/handback-payload.md`, `agent-lint.py --lint`.
