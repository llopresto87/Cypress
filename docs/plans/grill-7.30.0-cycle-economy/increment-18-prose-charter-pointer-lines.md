### Increment 18 — Prose: charter pointer lines
- Spec contracts: none here — increment 25 holds the pending-phrase contract over these files
- Files touched: `agents/00-orchestrator.md` (light variants adopted; stack step required; batch sizing, effort derivation, the ruling pass and the RED hash rule by pointer), `agents/01-architect.md` (the ruling pass and the amendment limits by pointer), `agents/02-implementer.md` (a batch in order; runs the tests; never edits a test or fixture), `agents/04-tester.md` (a RED batch sized by effort replaces "the first increment"), `agents/03-reviewer.md` (targeted tests plus the tip, by pointer), `templates/agent.template.md` (the light-variant sentence; its pointer `delegation.light-variants (docs/graph/method/delegation.md)` names `docs/graph/method/delegation-model-classes.md`)
- Tests to write (RED): none — prose increment
- Behavior added: the charters point at the cycle-economy leaf and restate none of it; every `description:` byte-stable
- Gate: `python3 tests/seed-lint.py` (eager surface unchanged); `python3 integrations/claude-code/agent-lint.py --lint --dir agents`; `python3 integrations/claude-code/agent-lint.py --eval --dir agents`
- Rollback path: revert
- Effort: medium
- Phase: prose
- Depends on: increment 8, increment 11
