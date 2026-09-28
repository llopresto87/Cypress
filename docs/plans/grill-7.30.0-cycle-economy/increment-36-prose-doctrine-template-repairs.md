### Increment 36 — Prose: doctrine and template repairs
- Spec contracts: none — accepted by review (SPEC-0005 AC-15, AC-16, AC-19)
- Files touched: `core/method/decision-economy.md` (:80 → `method.delegation-briefs`), `core/method/minimum-sufficient-work.md` (:60) and `core/method/engineering-posture.md` (:143) (→ `method.delegation-model-classes`), `core/method/vcs-posture.md` (:101 → `method.delegation-bounds`), `core/method/contract-posture.md` (:181 → `delegation.tracing` in `method.delegation-bounds`), `core/method/delegation-cycle-economy.md` (`delegation.question-file`: the ruling pass holds each ruling to the recorded design latitude), `core/method/delegation-model-classes.md` (:125-133: the Claude Code facts become one pointer to `integrations/claude-code/README.md`; reversed in increment 44), `templates/prompts/handback-payload.md` (:93-99: the stack-gap rule becomes a pointer to the bootstrap companion), `templates/agent.template.md` (:21-24 and :70-74: "SPEC-0005" becomes "the seed's SPEC-0005" or `delegation.effort`, and the Claude Code facts become a pointer), `templates/grill.template.md` (the Design latitude row's reversibility reads `reversible`), `protocols/test-first.md` (:249-253: a wrong test in a pure refactor is a question for the next tester spawn), `protocols/harvest.md` and `skills/toolcraft/SKILL.md` (`peers:` repointed to the leaf that holds the fact), `documentation/protocols-reference.md` and `documentation/skills-and-templates-reference.md` (the mirror rows the `peers:` edits require)
- Tests to write (RED): none — prose increment
- Behavior added: one home for the stack-gap rule; the latitude check at the ruling pass; the pure-refactor variant agrees with `delegation.green-self-test`
- Gate: `python3 tests/seed-lint.py` (leaf ceiling, mirrors); `prose-lint` per file against baseline
- Rollback path: revert
- Effort: medium
- Phase: prose
- Depends on: increment 29
