<!-- Increment 10 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 10: Prose: lane L7, the templates, and the new model map template `templates/docs/models.md` (ADR-0022), in the positive voice
- Item: the owner's instructions 1 to 3 (§2) over the templates, and the new model map template `templates/docs/models.md` (ADR-0022), under the round's rewrite conventions (kept outside the seed) and `skills/holistic-editing/SKILL.md`: closing prohibition lists folded into the sections that own their rules, "do X, because Y" in place of "do not", one home per rule, history narration out of doctrine, stale facts corrected
- Spec contracts: none: prose. No spec owns the voice of these files. Text a contract already pins is held by its existing check, and the final tip (increment 25) re-runs every one
- Files touched: `templates/*.template.md` (the eleven forms: adr, agent, data-contract, findings-report, grill, library-page, prompt-contract, skill, spec, threat-model, tool-page), `templates/knowledge-graph/_schema.md`, `templates/knowledge-graph/index.md`, `templates/knowledge-graph/node.template.md`, twenty-nine other leaves under `templates/docs/` (its README and index leaves, the runbooks, the node and session-record templates, `plans/grill.md` and `changelog.md`), and `templates/docs/models.md` (new)
- Tests to write (RED): none: prose. Routing text (`description:`, `routing_triggers:`, `title:`, `load_when:`) stays frozen, except a change the lane recorded with the router tests green; its negatives are listed for a later routing round (§12)
- Behavior added: none: the same rules, stated as the right move and its reason
- Gate: the lane's checks as its handback records them (kept outside the seed): `prose-lint.py --file` per file against its pre-edit copy, and the router or eval tests where the lane touched routing text; the full gate at the final tip
- Rollback path: `git checkout 7b219d7 -- <the files above>`
- Effort: high
- Phase: prose
- Depends on: increment 2
- Record: done 2026-09-30; its cross-lane items went to increment 13 or to the tooling wave
