# Slice 3 — brainstorm splits by audience

**Status:** implemented 2026-09-14, gate green. **Depends on:** nothing. Independent of slices 1, 2, 4
except for shared manifest/reference edits.

## Why

The only brainstorm the seed has **cannot exit without explicit user
confirmation** (evidence E7). So CYPRESS generating and comparing options
*against itself* — the divergent step before `grill` fills its options table and
before `adr-writer` records a choice — has no home anywhere in the graph.

Both of today's nodes are user-facing, so the protocol/skill pair does not draw
this seam. The U-40 evaluation proposed merging them on size (protocol 400
tokens < skill 650). Size is not a boundary; audience is.

The seam is clean, which is the evidence it is real: the Socratic machinery —
one-to-three questions per turn, reflect every two answers, a nine-question hard
cap, an eight-point convergence checklist — is **wholly inapplicable** with no
user to question. The two modes share a name and almost nothing else.

## Shape

One protocol, two modes, two technique skills beneath it — so "I need to
brainstorm" stays a single routing target and the router picks the mode from the
trigger.

| Node | Owns | Audience |
|---|---|---|
| `protocols/brainstorm.md` | `brainstorm.entry-and-exit` (**per mode**), `brainstorm.output-landing`, `brainstorm.mode-selection` (new) | both |
| `skills/brainstorm-socratic/SKILL.md` | `brainstorm-socratic.method` | **the user** — questioning, pacing, the cap, convergence |
| `skills/brainstorm-internal/SKILL.md` (new) | `brainstorm-internal.method` | **the session itself** — divergence against its own evidence |

## What each mode is

**Socratic (user-facing).** Unchanged in technique, plus one addition: it
**adopts `skill.humanizer`** for what it puts in front of the owner, so a person
reads what is being decided, why, and what it entails — not a bare options
table. `humanizer`'s charter already covers "briefs and reports for the owner";
it was simply never wired here (`brainstorm-socratic`'s `peers:` today are
`protocol.brainstorm` and `skill.spec-author`).

**Internal (self-facing).** No questions, no cap, no user. It generates
genuinely distinct options against evidence already in hand, states what would
have to be true for each, and names the one fact that would kill each. Its
exit is not user confirmation — it is a written options set that `grill` §7 or
an ADR's rejected-alternatives section can take verbatim.

The honesty risk is the point of the node: a session brainstorming against
itself will generate one real option and two strawmen. The skill owns the
discipline that stops that, and its exit condition is the check.

## Contract

- `AN_INTERNAL_BRAINSTORM_NEEDS_NO_USER` — the internal mode reaches its exit
  condition with no user turn.
- `A_USER_FACING_BRAINSTORM_IS_HUMANIZED` — the socratic mode's owner-facing
  output declares `skill.humanizer`.
- `EVERY_MODE_DECLARES_ITS_AUDIENCE` — `brainstorm.mode-selection` names the
  test that picks a mode, and both modes are reachable from the protocol.

## Regression, observed RED first

`tests/test-brainstorm-modes.py` (new):

1. both mode skills exist, resolve as graph nodes, and are reachable from
   `protocol.brainstorm` — **RED today**, `brainstorm-internal` does not exist;
2. `brainstorm-socratic` declares `skill.humanizer` — **RED today**;
3. the internal skill's exit condition contains no user-confirmation step, and
   the socratic skill's does — a characterization of the seam;
4. `brainstorm.mode-selection` is owned exactly once.

## Risk

**A third node where there were two**, against a roster the owner has already
called large. Accepted because it is the one slice that adds a node for work
that is genuinely happening and currently unowned — and net across the plan the
node count still falls.

**Mode confusion is the real failure**: a session using the internal mode where
the user should have been asked. `brainstorm.mode-selection` is where that is
prevented, so it carries the whole weight and must state a test, not a
preference.
