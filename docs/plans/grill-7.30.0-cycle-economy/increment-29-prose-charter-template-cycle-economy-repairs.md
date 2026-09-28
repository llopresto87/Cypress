### Increment 29 — Prose: charter, template and cycle-economy repairs (ruling pass 3)
- Spec contracts: none — accepted by review (SPEC-0005 AC-15)
- Files touched: `agents/02-implementer.md` ("After GREEN" step 2: the implementer does not clean up tests; test cleanup it finds is a question-file entry for the next tester spawn), `agents/04-tester.md` (REFACTOR: the tester cleans up tests in its own spawn with the suite green; the implementer refactors code only), `core/method/delegation-cycle-economy.md` (`delegation.green-self-test`: the REFACTOR sentence of SPEC-0005 §6), and the engineering-posture pointer repairs in `agents/03-reviewer.md` (:127), `agents/00-orchestrator.md` (:300), `agents/growth-orchestrator.md` (:132), `agents/13-ui-ux-designer.md` (:69), `agents/tool-smith.md` (:114), `templates/agent.template.md` (:123)
- Tests to write (RED): none — prose increment
- Behavior added: GREEN's test ban holds through REFACTOR; the merged T2 path (`tiers.execution-paths`) is unchanged; charters point at the leaf that holds each fact. Every `description:` byte-stable
- Gate: `python3 tests/seed-lint.py` (eager surface unchanged, leaf ceiling); `python3 integrations/claude-code/agent-lint.py --lint --dir agents`
- Rollback path: revert
- Effort: medium-low
- Phase: prose
- Depends on: increment 18
