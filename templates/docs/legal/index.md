# Legal & regulatory index

This file is the scope instruction for `agent.legal`: the one place that
says which of the instruments on disk bear on this project, which do not and
why, and what the corpus does not carry at all. It is a determination, it is
revised as the project evolves, and it is the *only* legitimate way to narrow
what the analyst considers.

One home per fact, and the line is strict. `corpus/` holds the **citation**:
what the rule says and how strongly that is sourced. The project's
**application** of the rule (which of its systems engage it, what was found,
what was decided) belongs to the owning node or decision record that makes the
claim, and cites the entry id.

`corpus/` beside this file is the seed's `legal-corpus/`, placed **whole** on
the owner's decision (`grow.legal-corpus`). Every page it ships is here or none
is. Mark an irrelevant page with an `out of scope` row below and keep the page
on disk; deleting it is the wrong move. The analyst has no web access, so a
page that is not on disk is indistinguishable from an instrument that does not
exist, and its `no corpus entry → no claim` rule would turn your import filter
into a confident "this does not apply" (`corpus/_schema.md` §"Whole corpus,
or none").

## Scope for this project

Every instrument the corpus carries gets a row. `in scope` means the analyst
reasons from it; `out of scope` means it does not, **for the stated reason**,
until someone changes this line.

| Instrument | Scope | Why — the project fact that decides it | Reviewed |
|---|---|---|---|
| <corpus page> | in scope / out of scope | <the evidenced reason, with a path> | YYYY-MM-DD |

## National layer — which jurisdiction, and whether it is carried

The corpus's EU and international pages are jurisdiction-neutral. Its
**national** pages are only as wide as what has been ingested, so this section
says which jurisdiction governs this project and whether `corpus/national/`
actually holds it. Where it does not, every national instrument belongs in the
table below as an ingest request: `agent.legal` refuses on them until a
`research-scout` pass lands them. Until then the analyst reasons only from the
governing jurisdiction's own statutes, because a neighbouring country's statute
read across looks authoritative and is wrong.

| Fact | Value |
|---|---|
| Established under | `<country>` (`.cypress/seed.json` → `legal_jurisdiction`) |
| Carried by `corpus/national/` | yes / **no — ingest pending** |
| Evidence for the establishment | `<path, or: owner's assertion, undocumented in the plant>` |

## Not in the corpus at all

An instrument this project plausibly engages that `corpus/` does not carry.
The analyst cannot reason about these and must refuse; that refusal is correct.
Each row is an ingest request, not a gap to be filled from memory.

| Instrument | Why it may apply here | Status |
|---|---|---|
| <name> | <the project fact that raises it> | `not recorded — ingest pending` |

## Project-authored leaves

Rows for anything this project authored beside the corpus — a contractual
regime the corpus does not cover, for instance.

| Instrument | Kind | Page | Provisions covered | Verified | Status |
|---|---|---|---|---|---|

## Before citing anything here

- **Grade each entry on its own sourcing.** One page may hold entries of very
  different sourcing strength. A page-level "verified" banner over mixed
  provenance is a falsification.
- **Re-check currency before each use.** Re-read the entry's `verified` date
  and status every time before relying on it; a citation that shipped once is
  not thereby current.
- **State the edition.** For any amendable instrument, record whether the text
  is the original or the consolidated version — an unamended reading of an
  amended rule reads exactly like a correct one.
- **Write `not recorded` for any unknown.** An article number, date, threshold,
  or URL comes from a corpus entry, never from memory; `not recorded` is a
  usable answer, a plausible guess is not.

Entry contract and the full field vocabulary: `_schema.md` in this directory if
the project keeps one, otherwise the seed's `legal-corpus/_schema.md`.
