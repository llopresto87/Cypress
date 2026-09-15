### Slice 13 — An install into a real repository (U-12)

**Tier:** T3. The installer had only ever been validated against pristine temp
directories. Two failures were reproduced against a non-pristine target.

**D1 — the crash left a half-installed target.** With `.claude` present as a
regular file, the install ran `place_kernel` and the entire `docs/graph/`
scaffold to completion and *then* died on a raw, unwrapped
`mkdir: ... Not a directory` — not the tool's own `die()`. The target was left
with a kernel, both root files and a full graph tree, and no `.claude/`: the
worst outcome available, because a half-installed plant looks installed.

Fixed with a preflight that runs once, after adapter expansion and **before the
first write**. It collects *every* offending path rather than dying on the
first, and it is adapter-scoped — installing `claude-code` alone is not refused
over a `.github` file it will never touch. A non-writable target now fails the
same way instead of surfacing a raw `Permission denied` from `cp`.

**D2 — a deliberate deletion was reverted in silence.** Deleting nodes from an
installed plant's `docs/graph/protocols/` and re-installing restored them with
no log line, no `.bak`, no warning. Re-adding a seed-owned node is correct — the
seed owns its machinery — but doing it silently is not: the plant cannot tell
the fast-forward re-created something it had removed on purpose.

The fast-forward now names what it re-created, and stays quiet on a fresh
install, distinguishing the two cases by whether `.cypress/seed.json` existed
before the run. It reuses the single canonical writer rather than adding a
second traversal of the tree.

**Pinned by** `tests/test-install-adoption.sh` (8 cases), whose D1 case asserts
the contract that matters: not merely that the install fails, but that **the
target is still empty afterwards**. Observed red before the fix.

### An unplanned finding: the guard that had to be narrowed, not weakened

Adding `docs/specs/` tripped `tests/test-knowledge-paths.sh`, which denies bare
`docs/<collection>/` paths so that a plant's knowledge stays under
`docs/graph/`. The check already exempted `decisions` and `plans` as the seed's
own self-docs; `specs` is the same category, and the seed has no `docs/graph/`
of its own to put them under.

The tempting fix — drop `specs` from the pattern — would have lost a real guard:
a protocol telling a plant to write to a bare `docs/specs/` is exactly the
violation the check exists for, and specs are more central than decisions or
plans. So the guard was narrowed by **search path** instead: the machinery the
seed ships is still scanned with `specs` in the pattern, and only the seed's own
`docs/` tree is scanned without it. Both violation classes were re-confirmed to
fail afterwards — a protocol naming the bare specs collection, and a seed plan
naming the bare runbooks collection — so the change is a narrowing, not a hole.
(Both examples are described rather than written out, because the guard greps
this file too and a quoted example is indistinguishable from a real reference.)
