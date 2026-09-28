<!-- Increment 45 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 45: Prose: the settled-facts rule in its owning node and in every brief
- Item: R5 (class P)
- Spec contracts: none for the doctrine; the pending BRIEF_TEMPLATES_BYTE_IDENTICAL baseline amendment of SPEC-0003 §4 is applied in this commit
- Files touched: `skills/context-router/SKILL.md` (`rule.knowledge`: which facts are settled, which can go stale, and the anchor line), `templates/prompts/graph-session-bootstrap.md` (step 4 gains the two sentences of ADR-0018's worker form), the five embedding templates `templates/prompts/{investigation,node-authoring,growth-scout,growth-author,clean-context-validation}-brief.md` (the same block, byte-identical), `docs/specs/SPEC-0003-per-prompt-injection.md` (the baseline amendment and one §12 entry)
- Tests to write (RED): none new: seed-lint's identity check across the five templates
- Behavior added: a worker treats graph facts as settled and checks a code fact only when its brief carries no quiet anchor line
- Gate: `python3 tests/seed-lint.py` PASS; `spec-lint.py` within budget; prose-lint on each file against a scratch-copy baseline
- Rollback path: revert the files
- Effort: medium
- Phase: prose
- Depends on: increment 29, increment 31, increment 40
