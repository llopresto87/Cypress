## 7.31.0 — RED waves ahead of GREEN, session records instead of harness memory, and every engine through graft (2026-09-28)

The owner asked for two things this release. Tester REDs should run ahead of
implementer GREENs as far as real dependencies allow, and what a session
learns should live in the plant, not in a harness's memory. A third
request made sure new and existing plants both receive the result. The design
latitude was balanced: one new owned rule, one read-only linter mode, and
nothing the goal did not ask for.

**Work runs in cycles (ADR-0012).** A RED wave writes every ready RED, spread
over as many tester spawns as the effort scale requires, and the scale's
per-spawn sizes do not change. A GREEN wave follows over the clean increments
only, with no ruling pass before it. The tip runs once the GREEN wave has
handed back. One ruling pass then covers every flag the cycle raised, and the
next cycle re-issues only the held increments, RED again where a ruling changed
their contract, together with whatever has become ready. The unit that pauses
is the increment, never the batch: an increment is held by an open question
that touches it, a RED that failed for the wrong reason or is under question,
or a tip failure blamed on it, and its dependents are held with it. Everything else proceeds. At the
tip, a RED whose GREEN has not committed is carried as expected-red by test
id, and nothing leaves the branch while any is carried. The rule's home is
`delegation.waves`, in `core/method/delegation-sequencing.md`. This supersedes,
in part, the owner's 7.30.0 decision O-5: its timing clause no longer holds
work that no question touches, and its one-pass, whole-picture ruling stands.

**`grill-lint.py --waves` prints the schedule.** It levels the plan's §9
increments into waves from their `Depends on:` rows, prints each with its
`Phase:`, and warns when two increments that no dependency orders name the same
file. It is a report: every existing check runs unchanged and alone decides
the exit status. A plan without `Phase:` fields prints `unscheduled`, and a
dependency defect leaves the schedule `not computed`.

**Harness memory is not a home (ADR-0013).** The kernel's §3.2 gains one
sentence: a session starts from the newest record in
`docs/graph/plans/sessions/` and writes what it learns there for canonize. The
full rule lives in `stewardship-posture.session-record`: which learnings count
(an owner rule, a corrected assumption, resume state), and that harness memory
keeps at most a pointer. Canonize takes each session record as a named input,
files its items or records why not, and hands back the harness entries that can
be retired; retiring one is the owner's decision, by name. The form ships to
every plant as `docs/graph/plans/sessions/_session-record.template.md`, and
growth-audit, like graft-audit, no longer reads an underscore form as an
unfilled scaffold. The Prime Agent overlay's close-out no longer sends
operating lessons to its own memory.

**A question put to the owner is as understandable as possible.** That is the
owner's standard, and `deliver.numbered-decisions` now holds the method that
meets it: before a choice is asked, say what the earlier decision says,
quoted; what changes, with one concrete example; what it costs; and what stays
the same. If the owner says the explanation fell short, explain again and
confirm before building on the answer.

**No worker moves a shared tree.** When several lanes write one working tree,
a worker runs no command that moves other writers' uncommitted files. It takes
a baseline by copying the file or reading it from `HEAD`, and each lane is
committed by pathspec (`delegation.lanes`).

**Seed text carries no session residue.** The seed's own `CLAUDE.md`
Conventions now say that its specs, plans, ADRs and doctrine name no session
identifier (a spawn id or a worker label) and no path to a round's working
records; a ruling is cited by its id. This governs work on the seed and ships
to no plant.

**Graft carries every graph engine (ADR-0014).** `tools/graft-graph-engine.py`
now takes each engine's own config when no `--preserve` is given: `ROOT_ID`,
`KINDS` and `KIND_PREFIX` for `graph-lint.py`, `TEST_GLOBS` for `spec-lint.py`,
and none for `grill-lint.py`. An explicit `--preserve` still wins. Before this,
the tool refused `spec-lint.py` and `grill-lint.py` unless the caller picked
the config by hand. `tools/graft-audit.py` accepts `--engine` more than once
and reports every pair on its own line, where it used to keep only the last.
Graft's Phase 3 and its engine and customization gates name all three engines.
SPEC-0001 now covers the engine reconciliation and the audit's engine check.

**Graft moves harness memory, and grow starts a record.** Graft gains a fourth
migration: it reads the plant's harness memory read-only, writes a first
session record listing every entry, and its own canonize close-out files the
record. It never edits harness memory itself. A growth session keeps its own
record from phase 1 and lists any memories the host already holds for the
project.

**Reach.** A new plant receives everything at install. An existing plant
receives the engines **by graft only**: `graph-lint.py`, `spec-lint.py` and
`grill-lint.py` are plant-owned once placed, and a plain re-install never
overwrites a placed engine, so a re-install alone leaves a plant without
`--waves`. Run a graft to take 7.31.0. Through graft, a plant also receives:
- the kernel's §3.2 sentence, with the kernel fast-forward, so its kernel diff
  adds it as expected;
- the session-record form under `docs/graph/plans/sessions/`, an expected new
  file that is no breach of the plant's own `plans/`;
- `delegation.waves`, the changed delegation-cycle-economy and
  stewardship-posture nodes, the changed canonize, deliver, graft, grow,
  recover and test-first protocols, and the orchestrator's and architect's
  charters;
- the memory migration, for a plant whose host holds memories for it.
