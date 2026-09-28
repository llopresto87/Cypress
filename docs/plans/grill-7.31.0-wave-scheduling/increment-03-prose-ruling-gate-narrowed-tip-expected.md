### Increment 3 — Prose: the ruling gate narrowed, and the tip's expected-red pointer
- Spec contracts: none — doctrine accepted by review (SPEC-0005 AC-19, which product amends at step 3, and product's new readiness-and-carry criterion)
- Files touched: `core/method/delegation-cycle-economy.md`: the ruling-pass paragraph of `delegation.question-file` becomes SPEC-0005 §6's "Ruling pass." text as re-ruled at ruling pass 0: one pass per cycle, after the clean GREEN wave, over every flag of the cycle; it rules on held increments only, by pointer to `delegation.waves` in the sequencing leaf. The `delegation.tip-cadence` paragraph gains the pointer clause of SPEC-0005 §6: the tip once per cycle after its GREEN wave, expected-red, and `not run`; `est_tokens` re-measured. No `owns:` change and no new `load_when`
- Tests to write (RED): none — prose increment
- Behavior added: the ruling pass stops holding clean work; it rules once per cycle on what was flagged
- Gate: `python3 tests/seed-lint.py` (leaf ceiling: the body stays at or under 170 lines; prevents overlap); `python3 tools/prose-lint.py --file core/method/delegation-cycle-economy.md` against its baseline count
- Rollback path: revert
- Effort: medium-low
- Phase: prose
- Depends on: none
