<!-- Increment 42 of `docs/plans/grill-7.32.0-harvest.md`; its §9 index row points here. -->

### Increment 42: Prose: the expertise composition rule points at its one home
- Item: A2 (class P')
- Spec contracts: none: template prose accepted by review
- Files touched: `templates/docs/nodes/_expertise.template.md`, `templates/knowledge-graph/index.md` (the composition sentence only)
- Tests to write (RED): none: prose
- Behavior added: both templates say the comparison is against the child's `load_when:` triggers and its slug, not body prose, and point at `skills/context-router/SKILL.md`, with no net growth
- Gate: `python3 tests/seed-lint.py` PASS; reviewer confirms no fourth phrasing of the formula
- Rollback path: revert both sentences
- Effort: low
- Phase: prose
- Depends on: increment 40
