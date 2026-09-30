<!-- Increment 7 of `docs/plans/grill-7.35.0-positive-voice.md`; its §9 index row points here. -->

### Increment 7: Prose: lane L4, the other fifteen protocols, in the positive voice
- Item: the owner's instructions 1 to 3 (§2) over the other fifteen protocols, under the round's rewrite conventions (kept outside the seed) and `skills/holistic-editing/SKILL.md`: closing prohibition lists folded into the sections that own their rules, "do X, because Y" in place of "do not", one home per rule, history narration out of doctrine, stale facts corrected
- Spec contracts: none: prose. No spec owns the voice of these files. Text a contract already pins is held by its existing check, and the final tip (increment 25) re-runs every one
- Files touched: `protocols/brainstorm.md`, `protocols/canonize.md`, `protocols/deliver.md`, `protocols/from-scratch.md`, `protocols/grill.md`, `protocols/grow.md`, `protocols/ingest-library.md`, `protocols/initialize.md`, `protocols/recover.md`, `protocols/specify-joint-pass.md`, `protocols/specify.md`, `protocols/test-first.md`, `protocols/verify-disagreement.md`, `protocols/verify-new-gates.md`, `protocols/verify.md`
- Tests to write (RED): none: prose. Routing text (`description:`, `routing_triggers:`, `title:`, `load_when:`) stays frozen, except a change the lane recorded with the router tests green; its negatives are listed for a later routing round (§12)
- Behavior added: none: the same rules, stated as the right move and its reason
- Gate: the lane's checks as its handback records them (kept outside the seed): `prose-lint.py --file` per file against its pre-edit copy, and the router or eval tests where the lane touched routing text; the full gate at the final tip
- Rollback path: `git checkout 7b219d7 -- <the files above>`
- Effort: high
- Phase: prose
- Depends on: increment 2
- Record: done 2026-09-30; its cross-lane items went to increment 13 or to the tooling wave
