# Evidence — `protocols/harvest.md`

Mined from `CHANGELOG.md`, the plans, and the diff of every one of the 6 commits
that touched the file. Note the scope limit: git history begins at a squashed
import, so everything from 4.2.0 (harvest's creation) through 6.9.0 — where most
of harvest's scars were earned — exists **only in `CHANGELOG.md`**.

## Size and structure

576 → 658 body lines. **One jump: `b4de261` (6.13.0), +57 lines, 100% Phase 4 and
its downstream restatements.** Everything else in the entire git history is ≤ +13.

| sha | release | body | Δ |
|---|---|---|---|
| `6dde434` | import ≈6.9.0 | 576 | — |
| `c8706d7` | 6.9.1/2 | 577 | +1 |
| `b4de261` | 6.12/**6.13.0** | 634 | **+57** |
| `53f845a` | 6.14/7.0.0 | 647 | +13 |
| `e9c1896` | 7.5.0 | 650 | +3 |
| `d7588e2` | 7.15.0 | 658 | +8 |
| worktree | 7.16.0 | 658 | **0 — untouched** |

**The heading list is byte-identical across the entire git history** — 24
headings, zero added, removed, renamed or reordered. Growth is not distributed:

| Section | import | now | |
|---|---|---|---|
| Phase 4 — seed integrity gate | 25 | 82 | **+228%** |
| Quality bar | 18 | 29 | +61% |
| What you do not do | 21 | 28 | +33% |
| *everything else (~600 lines)* | | | **+3 lines total** |

## The gate that passed by reading its own protocol

6.12.0 promoted the `legal` analyst and asserted: *"**No change needed — the
machinery was present**; only the consuming expert was missing."*

Nine versions later: *"`install.sh` **never placed it. Not partially: not at
all.** Every plant ever grown got `docs/graph/legal/index.unfilled.md` and
nothing else, so the analyst designed around a corpus could reach no law
whatsoever, and the only act available to it was the refusal. A plant then
recorded that empty collection as `UNKNOWN — regulatory applicability is the
owner's determination`, which reads as a careful deferral and was in fact a tool
that was never wired up. **Nobody could see it, because the thing that was
missing was the thing nobody had.**"*

The availability gate — added one release *after* this false claim, in response to
a different incident — was satisfied by reading harvest's own withdraw-contract
prose. `harvest.md:302-328` still says *"Prove the reach for each"* with no
command. **harvest.md was not touched by the fix.**

## Faithful import failed on the most recent harvest

7.15.0's own integrity gate: *"Faithful import: **PASS after correction** — an
independent review found **four passages thinned out of their donors and one page
that had inverted its donor's contract outright**; all five were restored or
corrected before release."* Five defects the gate as written did not detect. The
instruction that produced the misses (`:293-301`, unchanged since `b4de261`) is
still in force, with no diff command and no fidelity measure.

## The tool-only fix, and the near-miss that proves the class

`tools/agnosticism-lint.py` — harvest's named *"mechanical floor"* — carried a
silent-skip defect for its entire life: an unreadable file was `continue`d with
no diagnostic and no exit-code effect, so **a file the gate could not read was
indistinguishable from a clean one.** Its skip even carried a rationale —
*"binary or unreadable: carries no prose"* — while the tool's default glob is
`*.md`, so the only thing it could skip was a markdown file it had failed to
read. *"A stale reason reads exactly like a considered one."* Fixed in the tool;
`harvest.md` received nothing.

The near-miss: when that tool was first created it was **deposited and not
wired**, found only because someone applied *harvest's own availability gate* to a
non-harvest release — *"no protocol node named it, and no plant received it, so an
agent running harvest would read 'grep the diff' and hand-roll one."* The fix was
applied to that one tool and never generalized, and `HARVEST_PROMPT.md` — a second
entry point into the same protocol — was left out of even that sweep.

## Seed contamination — the recorded incident

4.8.0: *"a full sweep found **project-identifying content that had reached the
seed from the projects it was authored and grown inside**: a host application's
name and absolute install path, an authoring fleet's internal component/file/config
names narrated as 'this project's X', **stack fingerprints and an identifying
count in the harvest logs**, and one concrete dependency version pin."*

Root cause was harvest's own output template, which *"prescribed recording 'from
`<plant lineage id>`' and 'generalized-from: `<plant surface>`' straight into the
seed's CHANGELOG."* Fixed in the text (`:95-122`, `:564-578`). The **gate** was
not — see `slice-07-agnosticism-gate-covers-the-seed.md` for the four holes and
the live leak still in the tree.

## The class sweep that was never done

6.1.0 fixed *"Phase 2 said 'apply both gates' while the protocol defines three —
now 'all three'."* Three siblings survive, untouched since import: `:415`,
`:471`, `:508`. The skill-corpus section `:539-562` names **no** gates at all.

The seed wrote `holistic-editing.class-sweep` in 6.14.0 against exactly this —
*"fixing the handed instance while known siblings keep the defect"* — and it has
never been applied here.

## Prose edited to match a defect instead of checking it

At `c8706d7` harvest's skill-corpus withdraw contract was **edited to describe
broken installer behaviour**. Fourteen versions later 7.15.0 identified it: *"the
withdraw contracts in `harvest`, `toolcraft`, `skill-corpus/README.md` and the
librarian's charter **had all quietly written the hole down as if it were the
design**."* Every `skill-corpus` availability PASS in that window was asserted
against a withdraw path that terminated at `docs/graph/` and never reached a
harness.

## Accretion — one rule, five homes

Each new Phase 4 gate was added to Phase 4, then repeated in the gate template,
then quality-bar-passes, then quality-bar-fails, then "what you do not do":

| Rule | Phase 4 | template | QB pass | QB fail | WYDND |
|---|---|---|---|---|---|
| faithful import | `:293-301` | `:617` | `:631-633` | `:646-647` | `:676-677` |
| availability | `:302-328` | `:618` | `:631-633` | `:644-645` | `:673-675` |
| plant untouched | `:329-334` | `:619` | `:634-635` | `:648-649` | `:678-679` |
| full `run.sh` | `:335-338` | `:620` | `:635` | `:650` | — |

The agnosticism rule has **eight** homes: `:3`, `:89-93`, `:95-122`, `:275-279`,
`:573-578`, `:615-616`, `:639-641`, `:663-666`. Each addition came from a real
incident; none replaced its predecessor.

The frontmatter `description:` (`:3`) is a ~250-word restatement of four sections
— and it is the **eagerly loaded** surface, which makes it the most expensive
duplicate in the file.

The five corpus sections are a five-fold template repetition: 202 lines, each
carrying the same four sub-headings.

## Phase 4 contradicts itself

`:350-352` — *"A gate that runs but asserts nothing is a green lie; **each check
names its command and result**"* — sits below five checks that name no command:
faithful import, availability, plant untouched, clean install, minimum-sufficient.

## Never changed since import

`:25-38` metaphor, `:40-56` trigger, `:58-71` when to invoke, `:73-93` the
agnosticism gate, `:95-122` what counts as a project reference, `:124-150`
durability, `:152-174` non-redundancy, **`:176-271` the flow and Phases 1, 2 and 3
entire**, `:354-359` Phase 5, `:361-461` library and legal corpus, `:463-496` tool
corpus, `:564-612` output format.

Set against the run record this is not uniform. **Harvest has run at least nine
times** — 4.5.0, 4.7.0, 4.9.0, 5.2.0, 5.3.0, 6.5.3, 6.12.0, 7.9.0, 7.15.0 — so
Phases 1–3 and the three gates are heavily exercised but never revised. The
corpus block is the opposite: 31% of the body, and the **skill- and agent-corpus
withdraw contracts have never been proven end to end** (*"Deferred until a
harvested plant proves the round trip"*), while the skill one was demonstrably
wrong for fourteen versions.

## Frontmatter

Three `owns:` facts; `harvest.availability-gate` added at `b4de261`. **202 lines
— 31% of the body, the five corpus sections — belong to none of them.** Those
contracts are what `grow`, `graft`, `ingest-library` and `toolcraft` consume, and
they are not addressable by the router as a fact.

`harvest.availability-gate` appears in exactly two places in the whole tree:
`harvest.md:12` and one CHANGELOG line. `documentation/protocols-reference.md`
still lists two facts and `est_tokens: 7000` (real: 8043) at both `:37` and
`:1641`.

`est_tokens` itself is accurate and has been maintained on every touching commit
— the one frontmatter field of the three files that has not drifted.
