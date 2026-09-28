<!-- Increment 19 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 19: Prose: the measured-cost baseline, before any always-loaded change lands
- Item: the gate for decision 8
- Spec contracts: none: a measurement. Why: the owner set measured cost, not byte budgets, as the gate for items 8a, 8b and 8c', and a baseline taken after them would measure nothing
- Files touched: none in the seed; the measurement record is kept with the round's working records outside the seed
- Tests to write (RED): none: measurement. The fixed prompt set, the plant and the run count are §12 questions 1 and 2; the default is four prompts (a one-line question, a lookup of where a tool is installed from, an expertise case, a spawn of a worker with no shell), three runs each, on a staged copy of one grown plant installed from the seed at this round's base commit, recording turns, cumulative tokens and `agent-lint.py --eval` confident-wrong
- Behavior added: none
- Gate: the record lists every run with its numbers and the exact seed commit and prompts; the owner's token budget for it (§4) is not exceeded
- Rollback path: none needed; nothing in the seed changes
- Effort: medium
- Phase: prose
- Depends on: increment 1
