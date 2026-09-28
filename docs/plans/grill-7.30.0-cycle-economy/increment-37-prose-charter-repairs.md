### Increment 37 — Prose: charter repairs
- Spec contracts: none — accepted by review (SPEC-0005 AC-16, AC-18)
- Files touched: `agents/00-orchestrator.md` (:156-159 light variants "never on a security surface"; the "Every brief names" list quotes the recorded design latitude; ~~item 7's handback field list names every field~~ item 7 points at `templates/prompts/handback-payload.md` for the field list instead of listing fields, one home per fact (amended at ruling pass 6; the writer applied it this way)), `agents/01-architect.md` (:194-197: the ruling pass holds rulings to the design latitude), `agents/10-research-scout.md` (:89 → `method.delegation-model-classes`)
- Tests to write (RED): none — prose increment
- Behavior added: AC-16 and AC-18 met in the charters; every `description:` byte-stable
- Gate: `python3 tests/seed-lint.py` (eager surface unchanged); `python3 integrations/claude-code/agent-lint.py --lint --dir agents`
- Rollback path: revert
- Effort: medium-low
- Phase: prose
- Depends on: increment 29
