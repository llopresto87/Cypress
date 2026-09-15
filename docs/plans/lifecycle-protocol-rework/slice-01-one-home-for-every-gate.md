# Slice 1 — one home for every gate

**Depends on:** nothing. **Blocks:** every other slice.

## The defect

A gate in these three protocols is written between two and eight times. Adding
one costs that many edits, in the same commit, and the diffs show it: every gate
added to `graft.md` since 6.12.0 appears twice in its own diff, once as Phase 7
prose and once as an integrity-gate template row.

Measured homes per rule:

| Rule | File | Homes | Locations |
|---|---|---|---|
| the agnosticism rule | `harvest.md` | **8** | `:3` (description), `:89-93`, `:95-122`, `:275-279`, `:573-578`, `:615-616`, `:639-641`, `:663-666` |
| completeness / "grown is not skeleton" | `grow.md` | **8** | `:167-170`, `:184-186`, `:191-192`, `:232-233`, `:250-258`, `:628-631`, `:673-674` + the loop diagram |
| external evidence / `research-scout` | `grow.md` | **6** | `:57-70`, `:122-128`, `:401-424`, `:494-502`, `:679-683` + delivery |
| one-home-per-dependency | `graft.md` | **4** | `:504-520`, `:513-514`, `:763-774`, `:969-971` |
| the rootstock line | `graft.md` | **4** | `:83-94`, `:131-134`, `:658-665`, `:940` |
| faithful import | `harvest.md` | **5** | `:293-301`, `:617`, `:631-633`, `:646-647`, `:676-677` |

Every one of these accreted: each addition came from a real incident and none
replaced its predecessor. The record shows the pattern directly — `graft.md`
gained *"But relocating is not reconciling"* at `:300` and then
*"A relocated-but-unreconciled expert is rootstock in name only"* at `:316`, both
in reaction to the **same** operator complaint, the second restating the first for
emphasis rather than integrating it.

## The change

**One gate table per protocol is the single home for every gate.** Columns:

| # | What it asserts | Command | On failure | Class |
|---|---|---|---|---|

`Class` uses the ADR-0003 vocabulary already in force: `hard` (the harness
refuses), `soft` (a contract refuses), `detective` (post-hoc), `judgment` (a
named human or agent decides, and no tool can).

Then, in each file:

1. **Phase prose points at the table** and stops restating gates. A phase says
   what it *does*; the table says what must hold before it closes. Where the
   phase carries a reason the gate exists — the scar — that reason stays in the
   phase, once, and is not repeated in the table.
2. **The output/record template's gate section becomes the table's result
   column**, not a second list of rows to keep in sync.
3. **The quality bar keeps only what is not a gate.** A "passes when…" bullet
   that restates a gate row is deleted; a bullet that states a judgment no gate
   makes is kept and marked `judgment` in the table with its owner.
4. **"What you do not do" keeps only prohibitions that are not gates.** A
   prohibition with a gate is one line pointing at the gate number.

## Deletions, named

Nothing is summarized away. Each of these is deleted because the fact survives
in the gate table:

- `harvest.md` quality-bar-pass and quality-bar-fail entries for faithful
  import, availability, plant-untouched and full-`run.sh` (`:631-650`) — four
  pairs, eight bullets.
- `harvest.md` "what you do not do" entries `:673-679` for the same three rules.
- `graft.md` quality-bar entries `:929-930`, `:940`, `:962-963`, `:969-971`
  restating the audit, the rootstock line, the engine gate, and
  one-home-per-dependency.
- `grow.md:232-233` — the second statement of *"template files existing at their
  paths is never coverage"*, 41 lines after the first at `:191-192`.
- `graft.md:513-514` — the forward reference to the Phase 7 gate from inside the
  Phase 4 rule, now a table row number.

**Not deleted**, and worth saying because it looks like duplication and is not:
`harvest.md`'s three gates (`:73-174`) are *definitions*, not gate rows. The
table cites them; it does not replace them.

## The guard, without which this regresses in one release

Slice 1 is a one-time cleanup unless something keeps it. Add to
`tests/seed-lint.py`:

`check_gate_single_home()` — for each file in `LIFECYCLE_NODES`, parse the gate
table, and require that each row's assertion key appears **exactly once** outside
the table. The key is an explicit `id:` per row (e.g. `graft.gate.backups`), not
a phrase match, because phrase matching is how the last drift check was fooled.

Red first: it must fail on the tree as it stands today, naming the eight
agnosticism homes. That is the proof it binds, in the idiom
`tests/test-seed-budgets.sh` already uses for the ceilings.

## Expected result

| File | before | after |
|---|---|---|
| `graft.md` | 992 | ~910 |
| `grow.md` | 712 | ~670 |
| `harvest.md` | 658 | ~600 |

And the thing that actually matters: **adding a gate becomes one edit.**
