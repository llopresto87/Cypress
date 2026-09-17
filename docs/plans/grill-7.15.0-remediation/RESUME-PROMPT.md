# Operating doctrine — the CYPRESS 7.16.0 specs, and the adversarial review loop around them

**Use this file as the opening instruction of a new session.** It is
self-contained: it carries the objective, the constraints, the state, the
defect classes six rounds of review have already established, and the
procedure. Everything it asserts about the repository is either re-derivable by
a command it names or is recorded in `HANDOFF.md` beside it. Where the two
disagree, re-derive and fix both.

---

## Scope

This doctrine governs work on the **CYPRESS seed** at `<the seed checkout>`
(`<seed remote>`, branch `main`), and specifically the
**review → fix → review loop over the seed's own two specifications**:

- `docs/specs/SPEC-0001-install-placement.md` — what `install.sh` may do to a
  target repository.
- `docs/specs/SPEC-0002-routing-contract.md` — what `--route` and `--eval` may
  claim about themselves.

It governs the specs, the contracts they name, the tests those contracts cite,
the checks that enforce them (`tests/seed-lint.py`,
`templates/knowledge-graph/spec-lint.py`, `tools/gate-registry.py`,
`tools/ratchet-lint.py`, `tests/run.sh`), and the prose in the repository that
restates any of it.

It does **not** govern: the roster merge/retire question (needs a grown plant),
U-36 graph routing, U-41 institutional memory, or the corpora — which are a
**recorded exemption** from specs, bounded to the corpora, per `CLAUDE.md`.

## Objective

Bring both specs to the state where **every contract is either backed by a test
that asserts that contract in the file the spec names, or is honestly marked
`pending`** — and where the checks that certify this have each been observed
failing on a deliberate mutation.

The target is not "the gate is green." The gate has been green through every
round of this loop while carrying false claims. The target is that **a false
claim in either spec would turn the gate red**, and that where it still would
not, the spec says so about itself.

## Hard constraints

These override anything below.

1. **Do not commit.** The owner's standing instruction: nothing is committed
   until the goal is cleared. HEAD stays at `d7588e2`. Work stays uncommitted on
   `main`.
2. **Never author a fact that did not happen.** This loop already produced one
   fabricated sign-off line ("signed 2026-09-14 when its RED landed") written to
   satisfy a linter. A check that cannot be satisfied honestly is a finding, not
   an obstacle. Record the gap; never invent the evidence.
3. **Review is delegated; fixing is not.** The session that holds the tree
   **orchestrates** — it spawns the reviewers as subagents, reads their reports,
   confirms or rejects each finding, and applies the fixes itself. It does not
   review its own work in place of a reviewer, and a reviewer does not edit. The
   separation is the point: a session that both writes and grades its writing
   produces neither a credible review nor an honest count.
4. **Freeze the tree for the duration of a review round, and mutate only a
   copy — ever, by anyone, reviewer or not.** Reviewers reading a file you are
   editing cannot produce a credible review; writes happen **between** rounds.
   And a mutation test runs against `cp -a` of the repo, never in place: the
   seed-integrity digest lives at the `tests/run.sh` level, so a single suite
   run under a mutation is unwatched. Patching `place_file` in place and
   running one suite appended to **128 seed files** before anything noticed —
   under `--symlink` every destination is a symlink pointing INTO the seed.
   End every mutation by asserting `git status --porcelain | wc -l` is
   unchanged. This rule was written for reviewers only, and that is exactly how
   it failed.
5. **One writer per file.** Subagents are welcome and encouraged; partition work
   by file. Two agents must never hold the same file.
6. **Git attribution on this repo carries no AI co-author trail**, ever. Author
   is always `l.lopresto.87@gmail.com`. (Relevant only if the owner later lifts
   constraint 1.)
7. **Edit the canonical home, never a copy.** `CLAUDE.md` lists them. A fact
   with two homes is the defect this repository exists to prevent; adding a
   second home to record a fix is the most common way this loop has regressed.
8. **Integrate; do not bolt on.** A fix belongs inside the structure of the file
   it lands in, sweeping every sibling view of the same fact. Name what you
   delete.

## Doctrine compatibility

This doctrine does not displace the repository's own. Where they conflict,
`CLAUDE.md` and the node that owns the fact win, and the conflict is reported
rather than silently resolved. In particular, preserve:

- **one home per fact**, and derive rather than transcribe any count;
- **append-only** `CHANGELOG.md` and `docs/decisions/`;
- the **kernel byte budget** (8 000) and the per-session instruction budgets;
- **ratchets may only tighten** (`tools/ratchet-lint.py`); a raised limit needs
  an owner decision, not a bless;
- `harvest`/`graft` are **user-sovereign** and nothing may trigger them;
- **the spec's `active` moment is the RED landing** (`verify.status-evidence`).
  A spec written after its behaviour is `back-written` and is never `active`,
  never signed, and never unchecked — `back-written` is in `LIVE_STATUSES`
  precisely so every check still runs on it.

## Current state, and how to re-derive it

Do not trust a number in prose — including in this file. Each row names the
thing that prints it.

| Fact | Command |
|---|---|
| every gate, what it READS, and the false green it can still produce | `python3 tools/gate-registry.py --summary` / `--table` |
| every ratcheted limit, and whether any loosened | `python3 tools/ratchet-lint.py --show` |
| routing accuracy per corpus class, never averaged | `python3 integrations/claude-code/agent-lint.py --eval --dir agents` |
| spec shape and contract coverage | `python3 templates/knowledge-graph/spec-lint.py --specs docs/specs --root .` — **without the flags it prints SKIP and exits 0**, which is how the seed's own specs went unchecked |
| roster justification, per node, derived | `python3 tools/roster-justification.py` |
| everything | `bash tests/run.sh` |

At the time of writing: **HEAD `d7588e2`**, `manifest.json` at 7.16.0, nothing
committed; last full gate EXIT=0 with 0 FAIL strings. Every other figure this
paragraph used to carry was wrong within hours — it said 40 gates against 41,
15 ratchets against 17, and 4 covered contracts where three careful hand counts
gave 4, 5 and 26 and the tool gives 7. Run the rows above; that is what they
are for.

`HANDOFF.md` carries the specification still owed and the decisions already
taken on how to implement it — §2 (what is open, what is blocked on a grown
plant, what is known-unfixable, and the disclosed residuals) and §3 (every
decision taken, with how it is implemented). Read both before acting. It was
stripped to that on purpose: the round-by-round narrative it used to carry is
not a specification, and a document that mixes the two is read as neither.

## Evidence requirements

Classify every conclusion before acting on it:

- **verified** — you ran the command, or mutated the property and watched the
  check go red, in this session;
- **documented** — a spec, ADR, or node asserts it, and you opened the file;
- **inferred** — follows from the above but was not observed;
- **unknown** / **contradictory** — say so, in those words.

Rules that follow from this, all of them learned the expensive way:

- **A check nothing would MISS is not kept.** Ask this beside the rule below,
  because "it goes red when I mutate the property" does not detect it: nine of
  thirteen `seed-lint` checks could be deleted outright with the whole gate
  green, including one added the same day whose three reds had been observed
  once by hand and re-observed by nothing. `tests/check-coverage-binder.py` now
  refuses a check with neither a planted violation nor a declared exemption.
- **A check that has never been seen red is not a check.** Three of the last ten
  checks added to this repository were inert: a regex demanding `agent.foo`
  where the document writes `foo`; an `re.S` that let `.*` span from an earlier
  heading; a `-type f` blind to symlinks. Each passed its suite. Mutate and
  observe RED, or report the check as unverified.
- **A test exiting non-zero is not evidence until you know why.** Build a
  wrong-reason guard into any test whose failure mode is ambiguous.
- **Opening the cited test is mandatory** for a §10 row. Two rows have already
  certified tests asserting something adjacent; both were found a round apart in
  the same table. A test whose assertion is substring presence does not assert a
  contract about content.
- **Re-derive every number, including one fixed last round.** Two figures
  shipped wrong in two consecutive rounds, each time because a fix moved the
  half that was right.

## Invariants

These must hold at the end of every round. Each names how it is checked.

1. **One home per fact.** — `tests/seed-lint.py`, and a manual sweep of sibling
   views in the same document.
2. **Every §10 row cites a test that asserts its contract, in the file named.** —
   `seed-lint`'s `check_spec_test_mapping`; binds the test name to the cited
   FILE, refuses `green` on a skipped test, refuses a row whose label cannot
   bind.
3. **No spec claims a promotion that did not happen.** — `spec-lint`, run over
   `docs/specs/` by `tests/run.sh`. Until round 7 this invariant was enforced by
   NOTHING: `spec-lint` resolved its paths from its own location, printed
   `SKIP`, and exited 0, so the fabricated sign-off could be re-landed with the
   whole gate green. Verified red now, six ways. When an invariant here names an
   enforcing file, open it and confirm the code is there — three of these were
   fiction.
4. **Every live spec carries at least one contract**, and an unknown `status:`
   cannot silence a spec. — `spec-lint` closed enum.
5. **Ratchets only tighten.** — `tools/ratchet-lint.py`.
6. **Every gate step is classified for the false green it can still produce.** —
   `tools/gate-registry.py` refuses an unclassified step.
7. **The seed's own tree is unchanged by its own gate.** — the run-level
   seed-integrity digest EXIT trap in `tests/run.sh`.
8. **Every machinery node carries `prevents:`**, and no two nodes' `prevents:`
   overlap past `PREVENTS_OVERLAP_CEILING`. — `tests/seed-lint.py`
   (`check_prevents_are_distinct`, all 1 770 pairs). The second half was fiction
   until round 7: the only ratio in the file compared a node's `prevents:` to
   its OWN `description:`, and copying one node's line byte-for-byte into
   another passed everything. That gap is why "moved collisions" recurred for
   five rounds — the brief asked REVIEWERS to do the sweep by hand.

## The five defect classes

Per-round finding counts are no longer tracked anywhere. They had five homes
carrying three different values, and the number was never load-bearing: a count
rises when the question gets harder and falls when it gets lazier, so it
measured the reviewers rather than the tree. The classes below are what
transferred; the counts were noise. Round 6's rise came from asking the
exhaustive question — every contract, every cited
test opened — rather than the incremental one. Expect that, and prefer it.

| Class | Why it recurs | Standing instruction |
|---|---|---|
| **repair drift** | a fix lands in one view; every reference document holds 2–3 views of a fact (summary table, per-node section, edge table, grouping) | after any fix, find the sibling views and sweep them; `check_reference_second_views()` covers only agents- and skills-reference — the other reference documents are unguarded |
| **inert checks** | a check is added, PASS is observed, and nobody verifies it FIRES | mutate every new check and watch it go red, in the same round it is added |
| **moved collisions** | rewriting a `prevents:` relocates a duplicate instead of closing it (`agent.implementer` collided three times and returned to its origin) | write the line about the node's own owned fact, not about the failure |
| **wrong-reason green**, and its inverse | a test exits non-zero for a reason other than the one it names — or a NEW check fires before the one a test exists to exercise and fails it with the new check's message. A wrong-reason RED hides a real check exactly as a wrong-reason green certifies a missing one; this was reintroduced in round 7 while adding a guard | build the wrong-reason guard into the test, and scope a new check to the harm it actually names |
| **an underived perimeter** | a check works exactly as described, inside a boundary nobody derived: a hand-written site list, a class gate, a status word, an `if uncovered:` branch, a `-P` default in `find`, a trigger phrase, a column-0 anchor. Round 8's governing result — round 7 applied "the checks work, their scope is the defect" to the checks it inherited and not to the checks it wrote | for every check, ask what it EXCLUDES and derive that boundary too. **Anything a check silently excludes is a place to hide**: a `prevents:` sweep that dropped short nodes hid the byte-copy it existed to catch, inside its own filter |
| **a diagnostic that never runs** | a branch that only executes on failure is untested by every passing run. M2's wrong-reason guard was dead code under `set -o pipefail` — `set -e` killed the script before it could print — and CI saw a naked exit 1 with an empty log | exercise the failure path itself, not only the property |
| **prose inversion** | any free-text assertion is satisfied by its own negation; natural-language negation is unbounded | **KNOWN-OPEN, NOT FIXABLE.** Recorded in `tools/gate-registry.py`. Report a count and one example; spend no round on it |

**The headline measurement, and the honest version of it.** Six behaviour
changes were inverted simultaneously and `bash tests/run.sh` was run. Before
review: 0 of 6 caught. After round 2 and stable since: **1 of 6** — the earlier
"4 of 6" was wrong and is corrected in `tools/gate-registry.py`. The one caught
is `initialize`'s entry fork, whose assertion is bound to **table cells**. The
survivors are prose. This is the governing empirical result of the whole loop:

> **Structural assertions — frontmatter keys, table cells, parsed router output,
> file hashes, exit codes — hold under mutation. Prose assertions never do.**
> Raising the cost of inverting a prose claim from verbatim to reworded does not
> change its class.

Every fix should therefore move an assertion **onto a structure**, or record
that it could not be moved.

## Decision rules

- **Fix when** the defect is structural, the cause is understood, and the repair
  can be observed red first. Prefer the smallest change that makes the false
  claim fail the gate.
- **Record rather than fix when** the assertion is prose-only, or when honest
  evidence does not exist. `pending` in a §10 row, an explicit exception in a
  spec's §4, and a false-green class in `tools/gate-registry.py` are all
  legitimate outcomes. A spec that says what it cannot prove is correct; a spec
  that implies proof it lacks is not.
- **Escalate to the owner when** a ratchet would have to be raised, when a
  contract's stated behaviour is wrong rather than merely unproven, or when the
  fix changes what a grown plant would receive.
- **Reject a change when** its justification is a principle rather than a
  demonstrated defect; when it adds a second home for a fact; when it moves
  complexity rather than removing it; or when it would make the gate green
  without making the claim true.
- **Contract falsification outranks drift.** A contract that is false of the
  code it describes is worse than ten stale sentences.

## Execution phases

### Phase 0 — Orient (no writes)

Read `HANDOFF.md` §2 and §3. Run the six commands in the state table. Reconcile what
they print against what §9 and this file say; every disagreement is a finding
before any other work starts.

### Phase 1 — Fix (tree is yours; no reviewers running)

Work `HANDOFF.md` §2's open list **worst first**: contract
falsifications, then mismapped §10 rows, then ratchet slack, then
self-contradictions, then under-scoped contracts, then repair drift, then the
digest hole. For each item:

1. Reproduce the defect; state the evidence class.
2. Make the smallest change that closes it, in the canonical home.
3. **Mutate and observe red** — the check must be seen failing.
4. Sweep sibling views of the fact you touched.
5. Strike the item in `HANDOFF.md` §2 with one line saying what was done and what was
   observed.

Partition across subagents by file. Never two writers on one file.

### Phase 2 — Freeze

Stop writing. Record the tree's state (`git status --porcelain | wc -l`, and the
digest if you have one). Nothing below this line touches a file until Phase 5.

### Phase 3 — Review (parallel, read-only, adversarial)

**Brief each reviewer with the SPEC and the file list, and nothing else.** Name
the contracts it must check and the files in scope. Do NOT say which files were
modified, what was changed in them, or why; do not hand over the previous
round's findings, this session's account of them, or a list of "fixes to
verify".

That is what made rounds 7 and 8 circle. A reviewer told "round 7 closed X by
doing Y" audits the SENTENCE — it re-derives the claim, checks the account for
internal consistency, and reports on the narrative. A reviewer given only the
spec and the files reads the artifact, and what it finds is independent of
whatever the previous round believed. The difference is not politeness about
bias; a reviewer handed the rationale cannot produce evidence the rationale did
not already anticipate.

Corollaries, both learned the expensive way:
- **Never state a number in a brief.** A brief saying "all six escape shapes
  refuse" gets the six checked and the seventh unlooked-for.
- **Constrain sub-agents explicitly.** A reviewer may spawn its own; say that
  every copy is per-agent and that no agent may read a copy another has
  mutated, or a finding can describe a sibling's mutation rather than the tree.


Spawn independent reviewers. Give each the spec and the file list — and, per the
briefing rule above, nothing about what changed or why — with a distinct remit so
their findings do not collide. The remits that have produced findings:

- **specs deep audit** — every contract, every §10 row, every cited test opened.
- **check integrity** — every check added since the last round, mutated.
- **repair drift** — every fix from the last round, swept across sibling views.
- **numbers** — every figure in prose re-derived from the tool that prints it.
- **contract truth** — does the code actually do what the contract says.

Require every finding labelled **[STRUCTURAL]** (fixable, fix it) or
**[PROSE]** (count only), with a file:line and the evidence class. A reviewer's
claim is itself a claim: **a reviewer has already been wrong once**, and only
checking caught it — two "new" misroutes routed identically at `d7588e2`. Keep a
baseline to hand and verify before acting.

### Phase 4 — Triage

Confirm or reject each finding against the evidence rules. Reject fabricated,
duplicated, and already-known-open findings explicitly, by name. Record the
confirmed count for the round.

### Phase 5 — Apply, and record

Unfreeze. Apply confirmed structural fixes. Update `HANDOFF.md` §2 (or the
next round's subsection) with what was applied, what is outstanding, and what
was rejected and why. Then return to Phase 2.

## Verification, proportional to risk

**Reading the gate.** Capture `bash tests/run.sh`'s own exit code by itself,
with nothing after it, and read the log before saying anything about the run.
Running it backgrounded as `run.sh > log; echo EXIT=$?; ...; tail` reports the
LAST command's status — `tail`'s, always 0 — and a red gate was announced as
green on exactly that. A verification procedure is a check like any other, and
that one had never been seen red.

| Change | Minimum verification |
|---|---|
| prose in a document | the sibling views swept; `bash tests/run.sh` |
| a new or edited check | the mutation observed red, plus the control run showing it green unmutated |
| a spec contract or §10 row | the cited test opened and read; the mutation of the contract's property observed red |
| a ratchet | `python3 tools/ratchet-lint.py --show` before and after; a raised limit escalated |
| `install.sh` or a placement path | `tests/test-install-placement.sh` against a real target, exit code asserted — not discarded |
| a router or corpus change | `--eval` per class, never averaged; both held-out sets unthinned |
| anything | `bash tests/run.sh` ending EXIT=0 with zero `FAIL` strings |

## Anti-patterns

- Editing a file a reviewer is reading.
- Adding a check and reporting it works because the suite passed.
- Satisfying a linter by asserting something that did not happen.
- Recording a fix in a new document instead of the fact's home.
- Averaging corpus classes, thinning a held-out set, or tuning a trigger to a
  golden row.
- Raising a ratchet to make a gate green.
- Blessing a ratchet without re-deriving what it measures.
- Re-litigating the spec status question without reading `HANDOFF.md` §4's three tried
  values.
- Spending a round on prose inversion.
- Treating a green gate, a passing suite, or a finding count going down as
  evidence of correctness. Round 6's count went **up** because the question
  finally got harder.
- Summarising `HANDOFF.md`'s slice records into a new section; that is a second
  home.

## Stop conditions

The loop ends when **all** of these hold, each verified in the same round:

1. A full review round produces **zero confirmed [STRUCTURAL]** findings across
   all five remits, on a tree that did not move during the round.
2. Every contract in both specs is either backed by a test that asserts it in
   the cited file, or marked `pending` with the reason stated.
3. Every check added during the loop has been observed red on a mutation.
4. Every number typed in either spec, in `HANDOFF.md` §9, and in this file
   either matches the tool that prints it or is replaced by the tool's output.
5. `bash tests/run.sh` ends EXIT=0, zero `FAIL` strings, every gate classified,
   no ratchet loosened, and the seed-integrity digest unchanged.
6. `tools/gate-registry.py` records every false green the gate can still
   produce, including the prose-inversion class and any remaining digest hole.

The loop does **not** end because the finding count fell, because a round was
expensive, or because everything left is hard.

## Required outputs

**Per round:** the confirmed finding count; the applied list with, for each, the
mutation observed; the outstanding list worst-first; the rejected list with
reasons; the round's entry in `HANDOFF.md` §2 and §3.

**At the end:** a statement of which contracts are proven and which are
`pending`; the gate's remaining false-green classes; the diff of what changed
across the whole loop; and an explicit list of anything the loop could not
close, in the words of what a future session would have to do.

**Never:** a report that says "all tests pass" without saying what a passing
test would have failed to catch.

## Required end state

Both specs describe the behaviour the code actually has. Each contract is
either mechanically defended or honestly marked as not. The checks that defend
them have each been seen failing. Every number in the repository's prose about
itself either comes from the tool that derives it or is named as typed. The gate
is green, and — the part that matters — **it would be red if any of that stopped
being true.**

The seed should not merely contain individually corrected files. It should
describe itself accurately as one document, enforce that description
mechanically wherever a structure can carry the assertion, and state plainly,
in its own gate registry, every place where it still cannot.
