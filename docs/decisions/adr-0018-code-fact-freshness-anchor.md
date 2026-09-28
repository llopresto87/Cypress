---
status: proposed
status_date: 2026-09-28
owner: seed steward
---

# ADR-0018: facts the graph states are settled; code facts are checked once per session against an anchor canonize records

## Status

See frontmatter, which is the single home. Filed 2026-09-28 for 7.32.0 by the
round's joint specify and grill pass, planned in
[`../plans/grill-7.32.0-harvest.md`](../plans/grill-7.32.0-harvest.md). The
owner ratified the round's scope; this record stays `proposed` until the
increments it names land. It supersedes no earlier ADR.

## Date

2026-09-28

## Context

Grow, ingest-library and canonize establish facts so that no later session has
to: a library's behaviour, a best practice, a known bug, a decision, an owner
rule, and claims about the plant's own code. Sessions re-derive and re-check
them anyway, and every tool turn re-sends the whole context, so each re-check
is paid many times over. The owner's rules:

> "one of the scopes of this project is to reduce the need for a model to have
> to think and figure out things because we already provide solutions and
> information ourselves from a stable, durable and grounded source on disk" (R3)

> "models should not reason on facts already provided/present in their context
> because we already establish them through growth and the docs/graph (unless
> the files/information regarding on-disk code is stale - but a fact regarding
> a language, a best pratice, a bug etc should not be rediscovered or checked)"
> (R5)

Only facts about the plant's own code can go stale, and only when the code
moved. A per-file staleness tool was proposed and withdrawn by the owner ("no
don't create a new mechanical"), who then gave the design:

> "the creation of a stale files mechanical tool would mean more context
> duplicated for a tool called at each file access. instead we should keep
> track of each branch repo/commit at canonize and compare it at the beginning
> of a task and check for on-disk wip and/or/if the branch or the commit has
> changed since the last session we initiated with a plant" (R6)

## Decision

1. A fact the graph states is settled: use it, never re-derive or re-check it.
   This is doctrine in the kernel's §3.2 and in `skill.context-router`
   (`rule.knowledge`), and step 4 of the worker bootstrap block carries it.
2. Canonize records an anchor: for every repository the plant governs, the
   branch, the commit and the content hash of each uncommitted path, in
   `.cypress/anchor.json`, written by `docs/graph/code-anchor.py --record`. The
   same command prints one line that canonize puts in the session record.
3. At session start, one comparison: `code-anchor.py --compare`, run by the
   hook each host already fires at session start (Claude Code's
   `status-hook.py`, Prime Agent's `status-extension.ts`). Nothing moved gives
   one short line. Movement gives the paths that moved, and only facts about
   those paths may be stale; there the code wins and the node is fixed in the
   same change. Paths under `docs/graph/` and `.cypress/` are the graph and its
   state, not code.
4. No anchor, an unreadable one, or a comparison that could not run gives a
   line saying code facts are unverified: the doubt resolves toward checking,
   as ADR-0010's inclusion rule does. Settled facts stay settled either way.

The kernel sentence, in the bytes ADR-0017 frees: "A fact the graph states is
settled: use it, never re-derive or re-check it. Facts about code are current
unless the session-start code-anchor line names their paths; there the code
wins, and the node is fixed in the same change."

The worker form, for step 4 of the bootstrap block, because a worker starts
clean and sees no session-start output: "A fact the graph states is settled:
use it, never re-derive or re-check it. Facts about code are current only where
your brief carries a code-anchor line saying no code changed; otherwise check
the code facts you rely on against the code."

## Consequences

- A session pays one subprocess and one line at start instead of re-checking
  facts turn after turn.
- Workers do not see session-start output. The bootstrap block's step 4 tells a
  worker that code facts are current only where its brief carries a code-anchor
  line saying nothing moved; with no line, it checks the code facts it relies
  on. The orchestrator pastes the line into the brief. The routing redesign
  still open with the owner may later deliver it at worker start; this decision
  does not depend on it and takes nothing from it.
- opencode has no hook; it reads the line from the newest session record,
  which the kernel already sends every session to. codex and github-copilot
  stay frozen.
- New plants get the tool at install; existing plants get it, and the hook
  changes, at their next graft. A plant with no anchor sees the not-recorded
  line until its next canonize.
- SPEC-0003 gains twelve contracts for the tool and the hooks, and SPEC-0001
  one for the tool's placement, all pending until their RED lands.
- No per-file check, no per-access tool, and no staleness lint exist.
- Tests that fail if this is reversed: the anchor cases of
  `tests/test-bound-hook.sh` (plan increments 7, 8, 30 and 31) and the
  placement case of `tests/test-full-install.sh` (increments 17 and 39).

## Alternatives considered

- **A staleness lint or a per-file freshness tool.** Withdrawn by the owner:
  it duplicates context at every file access.
- **Commit and branch only, without uncommitted work.** Rejected: a session
  that edits a file across two sessions without committing would be told
  nothing moved, which errs away from checking.
- **The anchor in the status register's output.** Rejected: the register lists
  lifecycle debt from frontmatter and has one responsibility; the anchor reads
  Git. Both still run from the same hook.

## Reversibility

`reversible`: the hook line and the tool can be removed in one release; the
anchor file is state, and nothing else reads it.

## References

- Spec: SPEC-0003 and SPEC-0001, pending blocks of §4
- Grill: plan §6 decisions 11 (withdrawn) and 12, §9 increments 7, 8, 17, 30,
  31, 39, 44 and 45
