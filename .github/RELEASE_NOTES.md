## 7.33.0 — proportionate checks: a check has to earn its place (2026-09-29)

The owner found that the seed's tests had grown as complex as the code they
check, and that the same habits reach the systems a plant builds, which end up
with too many checks in their automated runs and in their running code. The
seed had 32,735 lines under `tests/` against 11,125 in `install.sh` and
`tools/*.py`, about 2.9 to 1. That count is the symptom. The cause was in the
seed's rules. Nothing said how large a test may be, and `test-first.lean-suite`
called any size limit "never a quota". The tester wrote one test for every spec
§7 failure mode, so a longer spec meant a longer suite. Mutation proof and
planted violations applied to all code. Every escaped bug added a gate, every
gate was added to the automated runs, and the posture nodes stated fail-closed
and validate-before-write as defaults for delivered code.

**One principle, one home.** `skills/test-first/SKILL.md` now owns
`test-first.proportionate-checks`, which replaces `test-first.lean-suite`. A
check is a test, a gate, or a check inside delivered code. It exists only when
someone can name what breaks, and for whom, without it. A test costs less than
its subject, asserts one behavior and never re-implements the code under test;
a test that would need more code than its subject goes back to the caller
unwritten. Mutation proof and planted violations are kept for the classes
`delegation.mutation-at-end` makes mandatory, once per batch. A new check joins
a project's automated runs or its running product only when the owner decides
so, and the seed adds none by default. Spec §4 contracts still get one test
each, because `spec-lint.py` holds every live contract to a named test.

**The other nodes link to it.** The tester charter tests a §7 failure mode only
where its blast radius is real. `protocols/verify-new-gates.md` asks for a new
gate only when a kind of bug recurs or its blast radius is high, and keeps two
duties for a gate script: it never leaves a half-applied state, and it keeps an
environment failure apart from a repository failure. The release posture adopts
supply-chain gates one by one where the blast radius is named, instead of four
by default. The engineering posture, the implementer charter and toolcraft size
runtime checks and tool tests by the same rule. The verification runbook
template starts with one blank row instead of eight gates.

The owner settled three follow-ups in the same batch. Outside the mandatory
classes no mutation pass runs unless the owner widens it to a named sample, and
the choice is recorded (`delegation.mutation-at-end`). A binding rule counts as
a control only once a gate enforces it, and that now applies to rules whose
breach has a high blast radius. Four older mentions of a specific runner or
delivery mechanism in `protocols/test-first.md`, `agents/04-tester.md`,
`protocols/verify.md` and `core/method/release-posture.md` now use neutral
words.

Fourteen files changed and the text is 10 lines shorter overall. No test was
added or deleted. The seed's own suite has not yet been reviewed against the
principle; that review is the next piece of work, and every deletion it proposes
waits for the owner to confirm it by name. Plants pick the change up by graft.
The plan of record is `docs/plans/grill-proportionate-checks.md`.

**The seed's own suite, consolidated under the principle.** Four reviewers
read every test against `test-first.proportionate-checks`, and the owner asked
that nothing be deleted that could be simplified, folded or deduplicated first.
The plan of record is `docs/plans/grill-test-consolidation.md`. Its §4 listed
97 cuts that drop an assertion. The owner accepted 94 as proposed, kept one
(the claude-code install into a directory with `&` in its name) and narrowed
two: `test-tier-lanes.sh` shrinks to one check that `tiers.contained-lane` and
`canonize.why-record` each have exactly one owner, and the per-suite test-count
floors go without a replacement file.

Measured at the end, with `wc -l` and one full gate run:

| Measure | Before | After |
|---|---|---|
| `tests/` lines, fixtures excluded | 32,760 | 16,015 |
| `tests/fixtures/` lines | 2,282 | 1,098 |
| `bash tests/run.sh` | 50 steps, 48 passing, 73.6 s | 45 steps, all passing, 26.0 s |
| Check lines per subject line | about 2.17 | about 1.06 |

The subject in the last row is about 15,100 lines: `install.sh` (2,561),
`tools/*.py` (8,427), `templates/knowledge-graph/*.py` (2,792) and the
integration hook scripts (1,320). That is a wider count than the 11,125 lines
quoted above, so the two ratios are not comparable. `tests/seed-lint.py` went
from 5,841 lines to 2,206, and `tests/test-seed-lint.sh` from 3,373 to 263. It
is now a table runner of 91 planted rows.

What changes for a maintainer:

- Nine suites are gone: `test-knowledge-paths.sh`, `test-orchestration-entry.sh`,
  `test-entry-paths.sh`, `test-graph-artifacts.sh`, `test-seed-budgets.sh`,
  `test-collected-count.sh`, `test_brainstorm_modes.py`,
  `test_tool_authorship.py` and `test_metadata_equivalence.py`. The knowledge
  path patterns are now rows of seed-lint's text-rules table.
- Four are new. `test-bound-hook.sh` keeps only the bounded-execution guard.
  The prompt-hook cases moved to `test-prompt-hooks.sh`, and the code-anchor
  cases to `test-code-anchor.sh`. The `verify-ledger.py` cases left
  `test-grill-lint.sh` for `test-verify-ledger.sh`, and the ratchet refusal
  cases left `test-seed-lint.sh` for `test-ratchet-lint.sh`.
- `tests/helpers/plant.sh` installs once per suite and copies the install for
  each case. `tests/helpers/lintcase.sh` holds `expect_rc`, `mini_tree` and
  `collect_case`. No suite copies the whole seed tree any more.
- The coverage binder (`tests/check-coverage-binder.py`) and the floors file
  (`tests/collected.json`) are gone. A new seed-lint check needs one planted
  row, seen red once. When a Python suite shrinks, nothing needs lowering. Its
  `Ran N tests` line in the gate log shows the count, and `unittest` exits 5
  when a suite collects nothing.
- The ratchet registry has one home, `tests/ratchets.json`, where each limit
  names its direction and its source file. Retiring a limit takes two edits,
  the constant and its lock entry. Twelve limits were retired and one added
  (`HOOK_TEXT_MAX_BYTES`), which leaves 22.
- The gate needs Python 3.11 or later, because a codex case parses TOML with
  `tomllib`, and its fallback for older versions is gone. That matches the floor the seed
  already recorded; CI still runs 3.12.
- Two bugs were fixed on the way. `test-legal-lint.sh` left its temporary
  copy of the tree behind, and the graft ledger case GR-h failed on any
  checkout whose version has a tag.

The owner accepted named coverage losses. They include most of SPEC-0004's
front-door wording checks, the review of stem collisions in the real routing
vocabulary, wording pins on protocol and skill prose, the test-count floors
(a suite that loses some of its tests now shows only as a smaller count in the
log), a seed-lint check that lands without a planted row, and several fixture
variants in the hook and ledger suites. §4 of the plan lists each loss with its
survivor, or says it has none.

Five specs were amended to match, each with a dated §12 entry. SPEC-0001 drops
its clauses on the host capability matrix's tier table. SPEC-0002 retires
`A_STEM_COLLISION_IS_REVIEWED_BEFORE_IT_SHIPS`. SPEC-0003 retires two source
checks and turns `HOOK_TEXT_RESTATES_NO_KERNEL_RULE` into a byte ceiling that
may only fall. SPEC-0004 goes from 22 contracts to 7 and from 2,347 lines to
760. SPEC-0005 moves from 0.13 to 0.14 and narrows six contracts. Where a
retired contract was cited by an earlier plan, that plan carries a dated
amendment (`docs/plans/grill-7.32.0-harvest/increment-53-final-tip.md`). No
installer, hook or linter behaviour changed.
