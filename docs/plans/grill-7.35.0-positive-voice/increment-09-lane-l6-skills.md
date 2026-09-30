<!-- Increment 9 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 9: Prose: lane L6, the fifteen skills, in the positive voice
- Item: the owner's instructions 1 to 3 (§2) over the fifteen skills, under the round's rewrite conventions (kept outside the seed) and `skills/holistic-editing/SKILL.md`: closing prohibition lists folded into the sections that own their rules, "do X, because Y" in place of "do not", one home per rule, history narration out of doctrine, stale facts corrected
- Spec contracts: none: prose. No spec owns the voice of these files. Text a contract already pins is held by its existing check, and the final tip (increment 25) re-runs every one
- Files touched: `skills/adopt-existing/SKILL.md`, `skills/adr-writer/SKILL.md`, `skills/brainstorm-internal/SKILL.md`, `skills/brainstorm-socratic/SKILL.md`, `skills/context-router/SKILL.md`, `skills/grill-planner/SKILL.md`, `skills/holistic-editing/SKILL.md`, `skills/humanizer/SKILL.md`, `skills/knowledge-graph/SKILL.md`, `skills/library-wiki/SKILL.md`, `skills/research-and-ingest/SKILL.md`, `skills/spec-author/SKILL.md`, `skills/test-first/SKILL.md`, `skills/toolcraft/SKILL.md`, `skills/validate-knowledge/SKILL.md`
- Tests to write (RED): none: prose. Routing text (`description:`, `routing_triggers:`, `title:`, `load_when:`) stays frozen, except a change the lane recorded with the router tests green; its negatives are listed for a later routing round (§12)
- Behavior added: none: the same rules, stated as the right move and its reason
- Gate: the lane's checks as its handback records them (kept outside the seed): `prose-lint.py --file` per file against its pre-edit copy, and the router or eval tests where the lane touched routing text; the full gate at the final tip
- Rollback path: `git checkout 7b219d7 -- <the files above>`
- Effort: high
- Phase: prose
- Depends on: increment 2
- Record: done 2026-09-30; its cross-lane items went to increment 13 or to the tooling wave
