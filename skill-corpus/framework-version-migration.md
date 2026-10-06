# Suggested skill: framework-version-migration

> Optional procedure — the behavior-preserving sequence for moving a codebase
> across a major generation of a framework, language runtime, or load-bearing
> dependency, so the jump lands with behavior preserved, in increments a gate
> can bisect. Composes `verify`, `verify-disagreement`, `grill`,
> `adr-writer`, and `security` by reference. Parameterized by
> `<source-generation>` and `<target-generation>`. A stack-keyed page under
> this corpus may specialize it for one framework; it adds only that
> framework's steps and restates none of these.

## When to apply

- A major version jump is forced (end-of-life, an unfixable-on-the-old-line
  advisory) and the target must behave as the source did.
- The codebase has little or no test coverage, so "it builds" is the only
  signal unless a safety net is built first.

**Prerequisite: a system you have seen working.** A system that does not run
today is first brought online, in a pass of its own. That pass is the only one
allowed to change behavior: it fixes or completes what is broken, and its
verified live state becomes the baseline this procedure preserves. Never
migrate a system you have not seen working, because a migration cannot
preserve a behavior nobody has observed. The role that runs that pass is
`agent-corpus/legacy-runtime-reconstructor.md`.

## The procedure

0. **Choose the target and the ceiling.** A generation already past its
   support end buys no runway as a landing. Split the jump at the first
   source-incompatible break: the highest generation reachable by build and
   configuration edits alone is one tier, and everything past the break is a
   modernization tier, one-way once merged, that needs its ADR (step 6)
   before its first commit. Tag each tier's reversibility. Crossing several
   generations in one pass is admissible; the break set to close is the union
   of every crossed generation's, paid in layers, so the first layer past the
   break is owed whatever the final target. Read the target's license before
   choosing it: a newer major of the same vendor can be a full rewrite under
   the same restrictive license that is the reason to leave the current
   version, and then the right first step is a license review, not the
   rewrite.
1. **Characterize first (RED spine).** Capture a baseline behavior oracle on
   the *pre-migration* code before touching anything — `verify-disagreement`'s
   behavior-preservation gate. No baseline ⇒ the preservation claim is
   unfalsifiable; on an untested codebase this baseline is the only real gate,
   and effort estimates are floors. Record the existing suite **by test
   name**, built from an export of the committed tree in the same toolchain:
   the after-diff is a name diff, because a count can hold steady while a test
   is swapped out. A guard written after the migration began counts only once
   it has run green on the pre-migration commit (`verify-disagreement`). A
   capability no in-process test observes (telemetry export, a metrics scrape,
   a broker binding) is read by an **external witness** now, with its time,
   because once the unit is migrated the before-reading cannot be taken.
2. **Stage into independently reviewable increments.** One concern per
   increment (namespace rewrite, security DSL, token handling, tracing…), each
   committed at its boundary with a rollback point (`grill` §9). A combined
   diff hides regressions; the full build+behavior gate is the *last*
   increment, not the first. Order the increments by the build graph: when the
   target raises the language runtime, that is the first increment; in-house
   artifacts built against the framework are rebuilt upstream first and
   republished before any consumer builds on them. Across a
   source-incompatible break this order is mandatory. Within one, a consumer
   can still resolve the newer versions at runtime, so an artifact left on the
   old line is recorded as a divergence and not as upgraded.
3. **Prove mechanical rewrites are complete.** For any large codemod, gate that
   no reference to the moved-set remains, no file holds a dual old+new path,
   and semantically-critical tokens were renamed not dropped (a dropped
   annotation compiles but silently bypasses). Run the census inside every
   repository that builds: a search from a parent directory that skips nested
   or ignored repositories under-counts and reads as complete.
4. **Enumerate consumers before any shared/unversioned contract changes.**
   Full producer + consumer set (plus second-order pass-through), migrated one
   participant at a time; canary-first on uniform multi-target changes.
   Enumerate by every way one can reach the contract, not by one symbol: a
   search for the shared symbol (a constant that holds a contract file's path,
   say) misses callers that pass that path explicitly, and a pipeline file
   that names the path as a literal through a
   template parameter is found by no code search. Classify each consumer
   (follows the shared symbol, or names the path itself) and assert that
   classification in a test. Coverage and classification are separate axes: a
   consumer pinned by a test can still be misclassified, and then no task
   converts it and no test goes red.
   Migrate one unit at a time only where the estate can run mixed; otherwise
   go lockstep. A shared library the units call keeps its entry signature
   identical across generations, with one release line per generation, so
   each unit moves, and rolls back, by a version bump alone.
5. **Gate on the intended-delta allowlist.** Diff against the baseline; accept
   only enumerated intended deltas, each justified as a strengthening, not a
   convenience relaxation (`verify-disagreement`). A test changes only through that list: a
   test edited to pass hides the drift the baseline exists to catch. A
   characterization test that breaks across the boundary may have lost its
   observation path, which sits on the moving stack too, rather than its
   behavior; measure which one moved before editing it
   (`verify-disagreement`, instrument first), and prove the adapted test by
   mutation. Clear the
   advisory/currency gate on the target (`security`).
6. **Record the decision and its escape hatch.** An ADR with the target, the
   reversibility class, and a documented fallback trigger (`adr-writer`).
   Every temporary arrangement the rollout creates gets its end condition in
   that ADR. A unit deliberately held back (say, a unit whose failure is a
   platform-wide outage and that has no baseline yet) names the event that
   brings it in; a compatibility wrapper or a fallback to an old name names
   the event that removes it. Without one, the held unit stays on an
   unsupported line and the wrapper becomes permanent indirection that
   operators keep calling.

## Reference files

- `protocols/verify.md` (RED by mutation, the three gate states)
- `protocols/verify-disagreement.md` (behavior-preservation gate,
  intended-delta allowlist, instrument first)
- `protocols/grill.md` / `skills/grill-planner/SKILL.md` (staged increments, rollback)
- `skills/adr-writer/SKILL.md` (the migration decision + fallback trigger)
- `agents/05-security.md` (advisory/currency + algorithm gates)
- `skill-corpus/maven/spring-boot-major-line-upgrade.md` and
  `skill-corpus/npm/angular-major-upgrade.md` (the stack-keyed pages that
  specialize this one)
