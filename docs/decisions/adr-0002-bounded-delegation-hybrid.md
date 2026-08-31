# ADR-0002: Bounded-delegation hybrid (5 delegators, leaf-only allowlists, depth ≤ 3)

## Status

`accepted` — implemented and verified 2026-07-13 (plan §9, P1).
**Amended 2026-07-23** (see *Amendment* below): the roster later grew to 16
agents and the number of opus delegators rose from five to **six**; the
bounded-delegation policy and its depth invariant are unchanged.

> This ADR is the standalone promotion of **ADR-B**, decided inline at
> `../plans/agent-routing-and-delegation.md` §3. The plan's §3 body remains the
> faithful source; this file restates it and links back. Do not re-decide here.

## Date

2026-07-13

## Context

The roster was **flat-by-tool-grant**: only 2 of 13 specialists (orchestrator,
multi-agent-architect) carried the `Task` tool, so the other 11 physically
could not spawn a sub-agent (plan §1, RC2). Their only moves at an out-of-domain
boundary were "hand back" or "do it myself." Worse, specialist prose told them
to "delegate to peer X" while no tool backed it (RC3) — under task pressure a
model reconciles that contradiction the cheap way and does the work inline. The
prose taught the over-reach it meant to prevent (problem B).

## Decision

Grant depth-capped `Task` to a **small set of opus coordinators** whose
definitions already name a legitimate sub-spawn, and keep **all leaf workers
Task-less**. Delegation tiers:

| Agent | `can_delegate` | `max_spawn_depth` | `delegates_to` (allowlist) |
|---|---|---|---|
| orchestrator | true | 3 | (all specialists) |
| multi-agent-architect | true | 2 | architect, tester, implementer, reviewer, data-ml, security, reliability |
| architect | true | 1 | tester, research-scout |
| reviewer | true | 1 | security, reliability |
| docs-librarian | true | 1 | research-scout |
| implementer, tester, security, reliability, data-ml, product, research-scout, pentest | **false** | 0 | — (leaf; STOP + handback) |

**Invariant:** an agent's `delegates_to` may name only agents whose
`max_spawn_depth` is strictly less than its own. A depth-1 delegator can
therefore reach only depth-0 leaves. The deepest legal chain is
orchestrator(3) → multi-agent-architect(2) → architect(1) → leaf(0) = depth 3.

## Consequences

- Three agents gained `Task` in P1 (architect, reviewer, docs-librarian) plus
  `max_spawn_depth` + `delegates_to`; the 8 leaves were set `can_delegate: false`
  with no depth/allowlist fields.
- The 5 RC3 prose lines were reconciled to match tools (reviewer×2, architect,
  implementer, tester) — every "delegate to peer X" now maps to a `delegates_to`
  entry or is rewritten to STOP + handback.
- `agent-lint.py --lint` now enforces the strictly-decreasing-depth allowlist
  invariant; tester added 4 ADR-B depth-invariant negative regression guards.
- The **leaf agents' absence of `Task`** is the one hard, harness-enforced
  recursion cap (they literally cannot spawn) — see ADR-0003 for why the numeric
  caps themselves are soft.
- Reversible per agent (remove `Task` + the frontmatter caps).

## Alternatives considered

- **Strict-flat + enforced handback for everyone.** — rejected: kills the RC3
  ergonomics, multiplies orchestrator round-trips, and makes the orchestrator the
  single point of routing failure that RC1 already indicts.
- **Give every opus agent `Task`.** — rejected: the blast radius for fan-out is
  too large and it loses the leaf guarantee that makes the depth cap real.

## Reversibility

`reversible` — per agent, by removing `Task` from `tools` and deleting the
`max_spawn_depth` / `delegates_to` frontmatter.

## Amendment (2026-08-06) — seventeenth agent, delegator count unchanged

The roster is now **17 agents**: `devils-advocate` joined the base roster,
promoted from `agent-corpus/` on the grounds that its mandate is universal
(every project produces claim-bearing deliverables) and no existing agent
covered it — `reviewer` audits a *changing diff* and holds no opinion on the
truth of a finished claim.

**This decision's invariant is untouched.** `devils-advocate` is a **leaf**
(`can_delegate: false`, no `Task`), so the delegator count stays at six and the
depth cap is unaffected. It is also read-only by construction — its `tools:`
grant carries no `Write` or `Edit`, keeping attack and repair structurally
separate — so it adds no write surface either.

Supersedes the "**16 agents**" count in the 2026-07-23 amendment below; that
figure was correct on its date and is left as written, per the append-only rule
for `docs/decisions/`.

## Amendment (2026-07-23) — sixth delegator, same invariant

Since this decision, the roster grew past the original 13 to **16 agents**,
adding the cross-project growth/graft/harvest meta-loop agents
(`growth-orchestrator`, `growth-scout`, `seed-installer`) and `pentest`. One of
these, **`growth-orchestrator`**, coordinates the growth meta-loop and so
carries depth-capped `Task` (`can_delegate: true`, `max_spawn_depth: 2`,
`delegates_to:` growth-scout, seed-installer, docs-librarian, architect,
research-scout, tester). That makes **six** opus delegators, not five:
orchestrator, multi-agent-architect, growth-orchestrator, architect, reviewer,
docs-librarian.

The decision itself is unchanged. Delegation is still granted only to a small
set of opus coordinators whose charters name a legitimate sub-spawn; leaves stay
Task-less; and the **strictly-decreasing-depth allowlist invariant still holds**
— growth-orchestrator(2) reaches only lower-depth targets (architect and
docs-librarian at 1; growth-scout, seed-installer, research-scout, tester at 0).
`agent-lint.py --lint` machine-enforces that invariant, so the roster cannot
drift out of compliance silently. Only the *count* of delegators changed; the
policy did not.

## References

- Plan (source of the decision): `../plans/agent-routing-and-delegation.md`
  §3 ADR-B, §4.1 (schema), §5 (per-file frontmatter + RC3 edits), §6 P1, §7
  (runaway-fan-out risk), §9.
- Sibling ADRs: `adr-0001-mechanical-agent-router.md`,
  `adr-0003-enforcement-layering-honesty.md`.
- Catalog: `index.md`.
- Carrier template: `templates/prompts/handback-payload.md`.
