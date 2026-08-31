# Suggested skill: framework-version-migration

> Optional procedure — the behavior-preserving sequence for moving a codebase
> across a major generation of a framework, language runtime, or load-bearing
> dependency, so the jump lands without silent behavior drift and without a
> big-bang no gate can bisect. Not a core skill; instantiate into
> `.claude/skills/` from `templates/skill.template.md` if selected. Composes
> `verify`, `grill`, `adr-writer`, and `security` by reference — it does not
> restate them. Parameterized by `<source-generation>` and
> `<target-generation>`.

## When to apply

- A major version jump is forced (end-of-life, an unfixable-on-the-old-line
  advisory) and the target must behave as the source did.
- The codebase has little or no test coverage, so "it builds" is the only
  signal unless a safety net is built first.

## The procedure

1. **Characterize first (RED spine).** Capture a baseline behavior oracle on
   the *pre-migration* code before touching anything — `verify`'s
   behavior-preservation gate. No baseline ⇒ the preservation claim is
   unfalsifiable; on an untested codebase this baseline is the only real gate,
   and effort estimates are floors.
2. **Stage into independently reviewable increments.** One concern per
   increment (namespace rewrite, security DSL, token handling, tracing…), each
   committed at its boundary with a rollback point (`grill` §9). A combined
   diff hides regressions; the full build+behavior gate is the *last*
   increment, not the first.
3. **Prove mechanical rewrites are complete.** For any large codemod, gate that
   no reference to the moved-set remains, no file holds a dual old+new path,
   and semantically-critical tokens were renamed not dropped (a dropped
   annotation compiles but silently bypasses).
4. **Enumerate consumers before any shared/unversioned contract changes.**
   Full producer + consumer set (plus second-order pass-through), migrated one
   participant at a time; canary-first on uniform multi-target changes.
5. **Gate on the intended-delta allowlist.** Diff against the baseline; accept
   only enumerated intended deltas, each justified as a strengthening, not a
   convenience relaxation (`verify`). Clear the advisory/currency gate on the
   target (`security`).
6. **Record the decision and its escape hatch.** An ADR with the target, the
   reversibility class, and a documented fallback trigger (`adr-writer`).

## Anti-patterns

- Editing tests to pass instead of enumerating intended deltas.
- A big-bang migration with no per-concern increments to bisect.
- Trusting "it compiles" as behavior preservation.

## Reference files

- `protocols/verify.md` (behavior-preservation gate, intended-delta allowlist)
- `protocols/grill.md` / `skills/grill-planner/SKILL.md` (staged increments, rollback)
- `skills/adr-writer/SKILL.md` (the migration decision + fallback trigger)
- `agents/05-security.md` (advisory/currency + algorithm gates)
