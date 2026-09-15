# The lifecycle protocols answer for themselves — a rework of graft, grow, harvest

**Status:** slices 1-6 implemented across all three files; slice 7 blocked on
one owner decision (§6, the redaction). Two rounds done: rework → adversarial
review (47 findings) → fix → re-review. Gate green, no limit loosened by these
slices. The step and limit counts are not restated here — ask
`python3 tools/gate-registry.py --summary` and
`python3 tools/ratchet-lint.py --show`, which derive them.
**Baseline commit:** `d7588e2` (7.15.0), working tree at 7.16.0
**Authorized by:** [ADR-0007](../decisions/adr-0007-lifecycle-protocol-ceiling.md),
which grants these three `LIFECYCLE_BODY_CEILING = 2500` on the finding that they
are "carrying procedure that is, if anything, **incomplete**", and names the
rework this plan is.

This file is the authoritative ledger. Each slice is a child file under
`lifecycle-protocol-rework/`; §6 indexes them and `seed-lint.py`'s
`check_plan_ledgers` enforces the bijection.

---

## §1 What this is for

ADR-0007 raised the ceiling on `protocols/{graft,grow,harvest}.md` from 1 000
lines to 2 500. That decision deliberately bought room rather than demanding
compression, on the argument that these are the only protocols that write into a
repository the seed does not own, and that truncating a destructive-operation
procedure to satisfy a line count trades a data-loss risk for a token-budget one
that is not even paid at this position in the graph — the router selects a node
from its `load_when:` triggers and never opens a body to decide whether it wants
the body.

Room is not a plan. This is the plan. It was written **after** the three files'
full recorded history was mined — every release entry in a 4 381-line CHANGELOG,
all 18 plans, the 7 ADRs, and the diff of every one of the 30 commits — rather
than from a reading of the current text. §7 holds that evidence.

## §2 The finding that makes this one rework and not three

**All three files grew the same way: one rule, written into N places.**

| Protocol | The mechanism | Worst case measured |
|---|---|---|
| `graft` | every gate is written once as Phase 7 prose and again as an integrity-gate template row — **so every gate added since 6.12.0 had to be written twice, in the same commit**, visible in every diff | one-home-per-dependency: **4 homes**; the rootstock line: **4** |
| `harvest` | every Phase 4 gate is written into Phase 4, the gate template, quality-bar-passes, quality-bar-fails, and "what you do not do" — **five** | the agnosticism rule: **8 homes** |
| `grow` | the same, spread across the contract section, the phase that performs it, and the Phase 6 check that verifies it | the completeness idea: **8 restatements**; `research-scout`: **3** |

This is the growth engine. It is also, precisely, the defect these protocols
exist to prevent: `graft.md:173` instructs a plant to *"collapse duplicate and
competing homes into one; trim every restated fact to a cross-reference"*, in a
file that states one of its own rules four times.

And it explains the growth curve. `graft` went 747 → 992 body lines (+33%) in 14
days; `harvest`'s heading list is **byte-identical across its entire git
history** while Phase 4 alone grew **+228%** and the rest of the file gained
three lines; `grow` has never shrunk in ten commits and 38 of its 55 original
paragraphs survive verbatim.

**Consequence for sequencing:** §6.1 comes first. Until one gate is one edit, no
other slice can land without paying the five-fold tax, and every slice below adds
gates.

## §3 The second finding: these procedures learn from people, not from their own gates

Sorting every recorded defect by who found it:

| Found by | Reached the protocol text? |
|---|---|
| a human operator on a live run | **almost always** — graft's six migration steps exist because one operator complained through four rounds; two of them exist because they complained about the *fix* |
| the seed auditing its own tooling | **almost never** |

The second row is ~28 defects whose protection lives entirely outside the
procedure. The sharpest three:

1. **`protocols/graft.md:677-679` has never been edited.** It reads *"the
   installer's backup behaviour is the safety net; **rely on it**"* — which is
   exactly the assumption the defining defect of 7.16.0 falsified. The installer,
   the audit and three test suites were rewritten around that sentence and the
   sentence was left alone.
2. **`install.sh` writes `docs/graph/plans/adopted-instructions.md`** when it
   overwrites a project's own instruction file. `graft.md` has never heard of it —
   and neither has `CHANGELOG.md`. A graft creates librarian work inside `plans/`,
   the one subtree graft's own audit is told to treat as untouchable, and never
   reports it.
3. **`tools/prose-lint.py` is installed into every plant** and `grow.md` never
   names it. Growth authors an entire graph of prose and never runs the linter the
   installer just handed the plant — the same defect class 7.13.0 closed for the
   seed's own front door.

## §4 The third finding: the honesty rule is stated inside the sections that break it

Both `graft.md:810` and `harvest.md:350` carry the same sentence — *"a gate that
runs but asserts nothing is a green lie; each check names its command and
result"* — and both are surrounded by checks that name no command.

| Protocol | Gate rows with no command |
|---|---|
| `graft` | 3 of 10, including `:910` "Backups present for every replaced file" — **the row that would have caught the defining defect, and it has no detector** |
| `harvest` | 5 of 8, including the availability gate, which is the one that failed |

`harvest`'s availability gate is the worst case on record: 6.12.0 asserted *"No
change needed — the machinery was present"* for the legal corpus, and nine
versions later the truth was *"`install.sh` **never placed it. Not partially: not
at all.**"* The gate had satisfied itself by reading harvest's own prose instead
of reading the installer.

## §5 Budget

The ceiling is 2 500. Nothing here is compression; §6.1 frees room and the rest
spends it.

| File | before | estimated | **actual** | headroom |
|---|---|---|---|---|
| `protocols/graft.md` | 992 | ~1 020 | **1 384** | 1 116 |
| `protocols/grow.md` | 712 | ~760 | **875** | 1 625 |
| `protocols/harvest.md` | 658 | ~680 | **922** | 1 578 |

The `actual` column is the body after frontmatter, counted the way
`seed-lint.py` counts it (`body.strip("\n").splitlines()`), re-measured
2026-09-15. It previously read 1 276 / 842 / 874, which did not reproduce
against the tree this ledger describes — the table was written mid-rework and
the rest of the rework landed on top of it. A budget table that does not
reproduce is worse than no budget table, because it is the one place a reader
goes to find out whether the ceiling is close.

**One of the three is over half the ceiling**, and the conclusion drawn from the
old numbers was false: half of 2 500 is 1 250 and `graft.md` is 1 384, at 55% of
its ceiling with 1 116 lines of headroom. The rule below still did not bite —
nothing here was compressed to fit — but "all three finish under half" was a
claim about slack, and graft does not have it. Every one overran its estimate,
by 15-36%, and the reason is worth recording rather than rounding away: **an
honest gate row is longer than a dishonest one.** A cell reading "PASS / FAIL"
costs four words; a cell naming the command, its flags, what the command cannot
establish, and who judges what it cannot, costs thirty. Slice 1's deletions were
real and did land — graft shed two parallel gate lists, harvest's quality bar
went from fifteen bullets to three — and slices 2 and 3 spent more than slice 1
freed.

The estimates were made before anyone had written a row. They should have been
made after writing three.

If a slice *would* break the ceiling, it is the slice that is wrong, not the
number — ADR-0007 says raising 2 500 is a fresh owner decision, never an edit
made to fit new text.

## §6 The slices

Dependency order. Each is a child file.

| # | Slice | Record |
|---|---|---|
| 1 | One home for every gate | `lifecycle-protocol-rework/slice-01-one-home-for-every-gate.md` |
| 2 | Every gate names its command, or declares itself judgment | `lifecycle-protocol-rework/slice-02-every-gate-names-its-command.md` |
| 3 | The procedures absorb their own tool fixes | `lifecycle-protocol-rework/slice-03-absorb-the-tool-only-fixes.md` |
| 4 | Class sweep — stale and self-contradicting text | `lifecycle-protocol-rework/slice-04-class-sweep-stale-text.md` |
| 5 | Reversibility, operationalized | `lifecycle-protocol-rework/slice-05-reversibility-operationalized.md` |
| 6 | The frontmatter describes the body | `lifecycle-protocol-rework/slice-06-frontmatter-describes-the-body.md` |
| 7 | The agnosticism gate covers the seed | `lifecycle-protocol-rework/slice-07-agnosticism-gate-covers-the-seed.md` |

## §7 Evidence

The mined history, per protocol, with citations. These are the input to every
slice above and the reason none of it was invented from a reading of the
current text.

| Protocol | Record |
|---|---|
| `graft` | `lifecycle-protocol-rework/evidence-graft.md` |
| `grow` | `lifecycle-protocol-rework/evidence-grow.md` |
| `harvest` | `lifecycle-protocol-rework/evidence-harvest.md` |

## §8 What this plan does not do

- **It does not split any of the three.** ADR-0007 settles that: the flow *is*
  the protocol, and a procedure read in pieces is worse than a long one read
  whole. Slice 1 removes duplication, it does not relocate sections.
- **It does not extract `graft.md`'s report template.** That remains open as
  HANDOFF Decision A, now optional rather than due. If it is taken, it lands
  after slice 1, when the gate table has settled what the record must carry.
- **It does not touch `U-36` (graph routing) or `U-41` (institutional memory).**
  Both need a grown plant.
- **It changes no tool behaviour except where a slice says so**, and each such
  change is named in that slice with its regression.
