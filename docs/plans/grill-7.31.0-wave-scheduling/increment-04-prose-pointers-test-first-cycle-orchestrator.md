### Increment 4 — Prose: pointers in the test-first cycle and the orchestrator's charter
- Spec contracts: none — accepted by review (product's readiness-and-carry criterion: `protocol.test-first`'s cycle points at `delegation.waves`)
- Files touched: `protocols/test-first.md` (`test-first.cycle`, the early-RED clause at :89-92 gains a pointer to `delegation.waves` in the sequencing leaf; an `OVERSIZED_LEAVES` member, so the clause is rewrapped within its paragraph and the body does not grow past `MACHINERY_BODY_CEILING`), `agents/00-orchestrator.md` (:261-274: one sentence saying work runs in cycles, a RED wave then a clean GREEN wave, holds are per increment, and early REDs are carried as expected-red at the tip, by pointer to `delegation.waves`; the words "the architect's ruling pass at each batch boundary" at :272 become "the architect's one ruling pass per cycle"), `agents/01-architect.md` (:194-199: "At a batch boundary, one ruling pass over the batch's question file" becomes "Once per cycle, after its clean GREEN wave, one ruling pass over every flag the cycle raised (`delegation.question-file`, `delegation.waves`)")
- Tests to write (RED): none — prose increment
- Behavior added: the two places a session reads its dispatch order point at the rule
- Gate: `python3 tests/seed-lint.py` (machinery body ceiling, stale pointers); `python3 tools/prose-lint.py --file <each file>` against its baseline count
- Rollback path: revert
- Effort: low
- Phase: prose
- Depends on: none
